"""
Interfaccia Grafica Principale - Chat Interface
Gestisce tutta l'interfaccia utente per l'applicazione RAG.

Componenti principali:
- Finestra principale con layout ottimizzato
- Area chat con messaggi scrollabili
- Pannello laterale fonti documentali
- Gestione citazioni interattive
- Popup per visualizzazione fonti
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Toplevel, Text
import os
import threading
import re
from typing import Dict, Any, List

from config.settings import AppTheme


class ChatApp(ctk.CTk):
    """
    Interfaccia grafica principale dell'applicazione.
    
    Gestisce:
    - Layout principale con pannelli separati
    - Chat interattiva con bubble messages
    - Pannello fonti documentali
    - Citazioni cliccabili
    - Popup per dettagli fonti
    """
    
    def __init__(self, backend):
        """
        Inizializza l'interfaccia grafica.
        
        Args:
            backend: Istanza del RAGBackend per le risposte AI
        """
        super().__init__()
        self.backend = backend
        
        # Configura finestra e layout
        self.setup_window()
        self.setup_layout()
        self.add_welcome_message()

    def setup_window(self):
        """Configura la finestra principale con titolo personalizzato."""
        self.title("🤖 Macchina delle Risposte - Consulente Normative Alimentari")
        self.geometry("1200x800")
        self.configure(fg_color=AppTheme.BACKGROUND)
        
        # Imposta icona se disponibile
        try:
            self.iconbitmap("assets/icon.ico")
        except:
            pass  # Ignora se l'icona non è disponibile
        
        # Configura la griglia principale
        self.grid_columnconfigure(0, weight=1, minsize=280)  # Pannello fonti
        self.grid_columnconfigure(1, weight=4)               # Area chat
        self.grid_rowconfigure(0, weight=1)                  # Area principale
        self.grid_rowconfigure(1, weight=0)                  # Footer

    def setup_layout(self):
        """Configura il layout completo dell'interfaccia."""
        self.setup_source_panel()
        self.setup_chat_panel() 
        self.setup_footer()

    def setup_source_panel(self):
        """Configura il pannello laterale delle fonti documentali."""
        self.source_frame = ctk.CTkFrame(
            self, 
            fg_color=AppTheme.CHAT_BACKGROUND, 
            corner_radius=10
        )
        self.source_frame.grid(
            row=0, column=0,
            padx=(10, 5), pady=10, 
            sticky="nsew"
        )
        self.source_frame.grid_rowconfigure(1, weight=1)
        
        # Titolo pannello fonti con icona
        title_label = ctk.CTkLabel(
            self.source_frame, 
            text="📚 Fonti Documentali", 
            font=AppTheme.FONT_TITLE,
            text_color=AppTheme.TEXT_COLOR
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        
        # Lista scrollabile delle fonti
        self.source_list_frame = ctk.CTkScrollableFrame(
            self.source_frame, 
            fg_color="transparent"
        )
        self.source_list_frame.grid(
            row=1, column=0, 
            padx=10, pady=(0, 15), 
            sticky="nsew"
        )
        
        self._populate_source_list()

    def setup_chat_panel(self):
        """Configura il pannello principale della chat."""
        main_chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_chat_frame.grid(row=0, column=1, sticky="nsew")
        main_chat_frame.grid_rowconfigure(0, weight=1)
        main_chat_frame.grid_columnconfigure(0, weight=1)

        # Area della cronologia chat
        self.chat_history_frame = ctk.CTkScrollableFrame(
            main_chat_frame, 
            fg_color=AppTheme.CHAT_BACKGROUND, 
            corner_radius=10
        )
        self.chat_history_frame.grid(
            row=0, column=0, columnspan=2, 
            padx=(5, 10), pady=(10, 5), 
            sticky="nsew"
        )
        self.chat_history_frame.grid_columnconfigure(0, weight=1)

        # Frame per input e pulsante
        input_frame = ctk.CTkFrame(main_chat_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(5, 10), pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        # Campo input con placeholder personalizzato
        self.entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="💬 Scrivi qui la tua domanda sulle normative alimentari...", 
            font=AppTheme.FONT_FAMILY, 
            height=45, 
            corner_radius=10
        )
        self.entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.entry.bind("<Return>", self._on_send_message)
        self.entry.bind("<Shift-Return>", lambda e: None)  # Blocca Shift+Enter

        # Pulsante invio
        self.send_button = ctk.CTkButton(
            input_frame, 
            text="📤 Invia", 
            command=self._on_send_message, 
            font=AppTheme.FONT_FAMILY, 
            height=45, 
            width=100, 
            corner_radius=10, 
            fg_color=AppTheme.PRIMARY_ACCENT,
            hover_color="#154c7a"
        )
        self.send_button.grid(row=0, column=1, sticky="e")

    def setup_footer(self):
        """Configura il footer con firma del creatore."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_propagate(False)  # Mantieni altezza fissa
        
        # Firma creatore
        signature_label = ctk.CTkLabel(
            footer_frame,
            text="© Tutti i diritti riservati • Powered By Zampier Zago",
            font=("Arial", 10, "italic"),
            text_color="#888888"
        )
        signature_label.grid(row=0, column=0, pady=8)

    def add_welcome_message(self):
        """Aggiunge il messaggio di benvenuto personalizzato."""
        welcome_msg = {
            "answer": "🎯 Benvenuto nella **Macchina delle Risposte**!\n\n"
                     "Sono il tuo Agente AI specializzato in normative alimentari. "
                     "La mia conoscenza si basa sui documenti ufficiali elencati nel pannello a sinistra.\n\n"
                     "💡 **Cosa posso fare per te:**\n"
                     "• Rispondere a domande su sicurezza alimentare\n"
                     "• Spiegare normative e regolamenti\n"
                     "• Chiarire aspetti di etichettatura\n"
                     "• Fornire informazioni su controlli sanitari\n\n"
                     "✨ **Le mie risposte includeranno sempre citazioni precise alle fonti utilizzate!**\n\n"
                     "Inizia pure con la tua prima domanda!",
            "source_documents": []
        }
        self._add_message(welcome_msg, "assistant")

    def _on_send_message(self, event=None):
        """
        Gestisce l'invio di un messaggio dall'utente.
        
        Args:
            event: Event di tkinter (opzionale)
        """
        prompt = self.entry.get().strip()
        if not prompt:
            return
            
        # Aggiungi messaggio utente alla chat
        self._add_message({"answer": prompt, "source_documents": []}, "user")
        self.entry.delete(0, "end")
        
        # Disabilita controlli durante elaborazione
        self._set_input_state(False)
        
        # Avvia elaborazione in thread separato per evitare freeze
        thread = threading.Thread(target=self._get_ai_response, args=(prompt,))
        thread.daemon = True
        thread.start()

    def _get_ai_response(self, prompt: str):
        """
        Ottiene la risposta AI in background.
        
        Args:
            prompt (str): Messaggio dell'utente
        """
        try:
            response_dict = self.backend.get_response(prompt)
        except Exception as e:
            print(f"Errore nella risposta AI: {e}")
            response_dict = {
                "answer": "⚠️ Mi dispiace, si è verificato un problema tecnico. Per favore riprova tra qualche istante.",
                "source_documents": []
            }
        
        # Torna al thread principale per aggiornare UI
        self.after(0, self._display_ai_response, response_dict)

    def _display_ai_response(self, response_dict: Dict[str, Any]):
        """
        Mostra la risposta AI nell'interfaccia.
        
        Args:
            response_dict (Dict[str, Any]): Risposta dal backend
        """
        self._add_message(response_dict, "assistant")
        self._set_input_state(True)
        self.entry.focus()

    def _set_input_state(self, enabled: bool):
        """
        Abilita/disabilita i controlli di input.
        
        Args:
            enabled (bool): True per abilitare, False per disabilitare
        """
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)
        self.send_button.configure(state=state)
        
        if not enabled:
            self.send_button.configure(text="⏳ Elaborando...")
        else:
            self.send_button.configure(text="📤 Invia")

    def _add_message(self, response_dict: Dict[str, Any], role: str):
        """
        Aggiunge un messaggio alla chat con stile appropriato.
        
        Args:
            response_dict (Dict[str, Any]): Contenuto del messaggio
            role (str): "user" o "assistant"
        """
        text = response_dict["answer"]
        sources = response_dict.get("source_documents", [])

        # Configurazione stile basata sul ruolo
        if role == "user":
            bubble_color = AppTheme.USER_BUBBLE
            padding = (80, 10)  # Allinea a destra
        else:
            bubble_color = AppTheme.ASSISTANT_BUBBLE
            padding = (10, 80)  # Allinea a sinistra
        
        # Frame contenitore per il messaggio
        bubble_frame = ctk.CTkFrame(self.chat_history_frame, fg_color="transparent")
        bubble_frame.grid(padx=5, pady=8, sticky="ew")
        bubble_frame.grid_columnconfigure(0, weight=1)

        # Crea messaggio con o senza citazioni
        if role == "assistant" and sources:
            self._create_message_with_sources(bubble_frame, text, sources, bubble_color, padding)
        else:
            self._create_simple_message(bubble_frame, text, bubble_color, padding, role)

        # Scroll automatico verso il basso
        self.after(100, self._scroll_to_bottom)

    def _create_message_with_sources(self, parent, text, sources, bubble_color, padding):
        """
        Crea un messaggio con citazioni interattive cliccabili.
        
        Args:
            parent: Widget parent
            text (str): Testo del messaggio
            sources (List): Lista dei documenti sorgente
            bubble_color (str): Colore di sfondo del messaggio
            padding (tuple): Padding per allineamento
        """
        content_frame = ctk.CTkFrame(parent, fg_color=bubble_color, corner_radius=15)
        content_frame.grid(padx=padding, pady=5, sticky="w")
        
        # Widget di testo personalizzato per gestire i bottoni
        text_widget = tk.Text(
            content_frame,
            bg=bubble_color,
            fg=AppTheme.TEXT_COLOR,
            font=AppTheme.FONT_FAMILY,
            wrap="word",
            borderwidth=0,
            highlightthickness=0,
            padx=15,
            pady=15,
            cursor="arrow",
            selectbackground="#4A4A4A"
        )
        
        # Trova pattern citazioni [doc-N] e sostituisci con bottoni
        citation_pattern = r'\[doc-(\d+)\]'
        matches = list(re.finditer(citation_pattern, text))
        last_end = 0

        for match in matches:
            start, end = match.span()
            
            # Inserisci testo normale prima della citazione
            text_widget.insert("end", text[last_end:start])
            
            # Crea bottone interattivo per la citazione
            doc_index = int(match.group(1)) - 1
            if 0 <= doc_index < len(sources):
                source_content = sources[doc_index].page_content
                source_metadata = sources[doc_index].metadata.get("source", "Fonte sconosciuta")
                
                citation_btn = ctk.CTkButton(
                    text_widget,
                    text=f"📄[{doc_index + 1}]",
                    font=("Arial", 9, "bold"),
                    fg_color=AppTheme.SOURCE_BUTTON_COLOR,
                    hover_color=AppTheme.SOURCE_BUTTON_HOVER,
                    height=22,
                    width=45,
                    corner_radius=4,
                    command=lambda content=source_content, meta=source_metadata: 
                        self._show_source_popup(content, meta)
                )
                text_widget.window_create("end", window=citation_btn)
            else:
                # Indice non valido, mostra testo normale
                text_widget.insert("end", match.group(0))
            
            last_end = end

        # Inserisci il resto del testo
        text_widget.insert("end", text[last_end:])
        
        # Rendi il widget di sola lettura
        text_widget.configure(state="disabled")
        text_widget.pack(expand=True, fill="both")

    def _create_simple_message(self, parent, text, bubble_color, padding, role):
        """
        Crea un messaggio semplice senza citazioni.
        
        Args:
            parent: Widget parent
            text (str): Testo del messaggio
            bubble_color (str): Colore di sfondo
            padding (tuple): Padding per allineamento
            role (str): Ruolo del messaggio ("user" o "assistant")
        """
        # Configurazione allineamento
        justify = "right" if role == "user" else "left"
        anchor = "e" if role == "user" else "w"
        sticky_pos = "e" if role == "user" else "w"
        
        # Etichetta del messaggio
        message_label = ctk.CTkLabel(
            parent,
            text=text,
            font=AppTheme.FONT_FAMILY,
            text_color=AppTheme.TEXT_COLOR,
            wraplength=600,
            justify=justify,
            fg_color=bubble_color,
            corner_radius=15,
            anchor=anchor
        )
        message_label.grid(padx=padding, pady=5, sticky=sticky_pos)

    def _show_source_popup(self, content: str, metadata: str):
        """
        Mostra popup con il contenuto dettagliato della fonte.
        
        Args:
            content (str): Contenuto del documento
            metadata (str): Metadati del documento
        """
        popup = Toplevel(self)
        popup.title(f"📄 Fonte Dettagliata - {os.path.basename(metadata)}")
        popup.geometry("750x550")
        popup.configure(bg=AppTheme.CHAT_BACKGROUND)
        
        # Centra il popup rispetto alla finestra principale
        popup.transient(self)
        popup.grab_set()
        
        # Header con titolo
        header_frame = ctk.CTkFrame(popup, fg_color=AppTheme.PRIMARY_ACCENT, height=50)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"📋 {os.path.basename(metadata)}",
            font=AppTheme.FONT_TITLE,
            text_color="white"
        )
        header_label.pack(expand=True)
        
        # Area di testo per il contenuto
        text_frame = ctk.CTkFrame(popup, fg_color=AppTheme.CHAT_BACKGROUND)
        text_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        text_area = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 11),
            relief="flat",
            bg=AppTheme.ASSISTANT_BUBBLE,
            fg=AppTheme.TEXT_COLOR,
            padx=15,
            pady=15,
            borderwidth=1,
            selectbackground="#4A4A4A"
        )
        
        # Scrollbar per il contenuto
        scrollbar = ctk.CTkScrollbar(text_frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Inserisci contenuto formattato
        text_area.insert("1.0", content)
        text_area.configure(state="disabled")
        
        # Footer con bottoni
        footer_frame = ctk.CTkFrame(popup, fg_color="transparent")
        footer_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        close_btn = ctk.CTkButton(
            footer_frame,
            text="✖️ Chiudi",
            command=popup.destroy,
            fg_color=AppTheme.ERROR_COLOR,
            hover_color="#d32f2f",
            height=35,
            width=100
        )
        close_btn.pack(side="right")
        
        copy_btn = ctk.CTkButton(
            footer_frame,
            text="📋 Copia",
            command=lambda: self._copy_to_clipboard(content),
            fg_color=AppTheme.PRIMARY_ACCENT,
            height=35,
            width=100
        )
        copy_btn.pack(side="right", padx=(0, 10))

    def _copy_to_clipboard(self, text: str):
        """
        Copia il testo negli appunti.
        
        Args:
            text (str): Testo da copiare
        """
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            print("✅ Contenuto copiato negli appunti")
        except Exception as e:
            print(f"❌ Errore nella copia: {e}")

    def _scroll_to_bottom(self):
        """Scorre automaticamente in fondo alla chat."""
        try:
            self.chat_history_frame._parent_canvas.yview_moveto(1.0)
        except:
            pass  # Ignora errori di scrolling

    def _populate_source_list(self):
        """Popola il pannello laterale con la lista delle fonti documentali."""
        data_path = "DATASET"
        
        try:
            if not os.path.exists(data_path):
                self._add_source_label("🚫 Cartella 'DATASET' non trovata", AppTheme.ERROR_COLOR)
                return
            
            # Trova tutti i file PDF nella cartella
            pdf_files = [f for f in os.listdir(data_path) if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                self._add_source_label("📭 Nessun file PDF trovato", AppTheme.ERROR_COLOR)
                return
            
            # Ordina i file alfabeticamente
            pdf_files.sort()
            
            # Header informativo
            info_label = ctk.CTkLabel(
                self.source_list_frame,
                text=f"📊 Documenti disponibili: {len(pdf_files)}",
                font=("Arial", 12, "bold"),
                text_color=AppTheme.SUCCESS_COLOR
            )
            info_label.grid(row=0, column=0, padx=10, pady=(0, 15), sticky="ew")
            
            # Aggiungi ogni file come elemento della lista
            for i, filename in enumerate(pdf_files):
                self._add_source_item(filename, i + 1)
                
        except Exception as e:
            print(f"Errore nel popolare la lista delle fonti: {e}")
            self._add_source_label("❌ Errore nel caricamento fonti", AppTheme.ERROR_COLOR)

    def _add_source_label(self, text: str, color: str):
        """
        Aggiunge un'etichetta informativa alla lista fonti.
        
        Args:
            text (str): Testo da visualizzare
            color (str): Colore del testo
        """
        label = ctk.CTkLabel(
            self.source_list_frame,
            text=text,
            anchor="w",
            font=AppTheme.FONT_FAMILY,
            text_color=color
        )
        label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    def _add_source_item(self, filename: str, index: int):
        """
        Aggiunge un singolo elemento fonte alla lista.
        
        Args:
            filename (str): Nome del file
            index (int): Indice per il posizionamento
        """
        # Frame contenitore per ogni fonte
        item_frame = ctk.CTkFrame(
            self.source_list_frame,
            fg_color="transparent",
            height=45
        )
        item_frame.grid(row=index, column=0, padx=5, pady=3, sticky="ew")
        item_frame.grid_columnconfigure(0, weight=1)
        item_frame.grid_propagate(False)
        
        # Tronca il nome file se troppo lungo
        display_name = filename
        if len(filename) > 28:
            name, ext = os.path.splitext(filename)
            display_name = f"{name[:25]}...{ext}"
        
        # Etichetta con icona e nome file
        file_label = ctk.CTkLabel(
            item_frame,
            text=f"📄 {display_name}",
            anchor="w",
            font=("Arial", 11),
            text_color=AppTheme.TEXT_COLOR
        )
        file_label.grid(row=0, column=0, padx=12, pady=8, sticky="ew")
        
        # Tooltip per nomi file troncati
        if len(filename) > 28:
            file_label.bind("<Enter>", lambda e, name=filename: self._show_tooltip(e, name))
            file_label.bind("<Leave>", lambda e: self._hide_tooltip())

        # Effetto hover
        item_frame.bind("<Enter>", lambda e: item_frame.configure(fg_color="#2A2A2A"))
        item_frame.bind("<Leave>", lambda e: item_frame.configure(fg_color="transparent"))
        file_label.bind("<Enter>", lambda e: item_frame.configure(fg_color="#2A2A2A"))
        file_label.bind("<Leave>", lambda e: item_frame.configure(fg_color="transparent"))

    def _show_tooltip(self, event, text):
        """
        Mostra un tooltip con il nome completo del file.
        
        Args:
            event: Event di tkinter
            text (str): Testo da mostrare
        """
        try:
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
            
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
            
            tooltip_label = tk.Label(
                self.tooltip,
                text=text,
                background="#333333",
                foreground="white",
                font=("Arial", 9),
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=4
            )
            tooltip_label.pack()
        except:
            pass

    def _hide_tooltip(self):
        """Nasconde il tooltip attivo."""
        try:
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                delattr(self, 'tooltip')
        except:
            pass

    def show_status_info(self):
        """Mostra informazioni sullo stato del sistema in un popup."""
        try:
            status = self.backend.get_system_status()
            
            popup = Toplevel(self)
            popup.title("📊 Stato Sistema")
            popup.geometry("500x400")
            popup.configure(bg=AppTheme.CHAT_BACKGROUND)
            popup.transient(self)
            
            # Area di testo per le informazioni
            info_text = tk.Text(
                popup,
                bg=AppTheme.ASSISTANT_BUBBLE,
                fg=AppTheme.TEXT_COLOR,
                font=("Courier", 10),
                padx=15,
                pady=15
            )
            info_text.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Formatta informazioni di stato
            status_info = f"""STATO SISTEMA RAG
{'='*30}

🔧 Componenti:
• LLM Principale: {'✅ Attivo' if status.get('llm_main_available') else '❌ Non disponibile'}
• LLM Router: {'✅ Attivo' if status.get('llm_router_available') else '❌ Non disponibile'}  
• Retriever: {'✅ Attivo' if status.get('retriever_available') else '❌ Non disponibile'}
• Catene: {'✅ Attivo' if status.get('chain_available') else '❌ Non disponibile'}

📊 Database:
• Documenti: {status.get('document_count', 'N/A')}
• Knowledge Scope: {status.get('knowledge_scope_items', 'N/A')} argomenti

🚦 Stato Generale: {status.get('status', 'Sconosciuto').upper()}
"""
            
            info_text.insert("1.0", status_info)
            info_text.configure(state="disabled")
            
        except Exception as e:
            print(f"Errore nel mostrare stato sistema: {e}")

    def clear_chat_history(self):
        """Pulisce la cronologia della chat."""
        try:
            # Rimuovi tutti i widget dalla chat
            for widget in self.chat_history_frame.winfo_children():
                widget.destroy()
            
            # Riaggiunge il messaggio di benvenuto
            self.add_welcome_message()
            
            print("✅ Cronologia chat pulita")
        except Exception as e:
            print(f"❌ Errore nella pulizia chat: {e}")