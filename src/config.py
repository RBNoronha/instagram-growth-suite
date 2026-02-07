"""
Configurações do Instagram Growth Suite
Centraliza todas as configurações do sistema
"""
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

@dataclass
class Config:
    """Configurações principais do sistema"""
    
    # ============================================
    # CREDENCIAIS
    # ============================================
    IG_USERNAME: str = field(default_factory=lambda: os.getenv("IG_USERNAME", ""))
    IG_PASSWORD: str = field(default_factory=lambda: os.getenv("IG_PASSWORD", ""))
    
    # ============================================
    # NAVEGADOR
    # ============================================
    HEADLESS: bool = field(default_factory=lambda: os.getenv("HEADLESS_MODE", "False").lower() == "true")
    BROWSER_TIMEOUT: int = field(default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30")))
    CUSTOM_USER_AGENT: str = field(default_factory=lambda: os.getenv("CUSTOM_USER_AGENT", ""))
    PROXY_URL: str = field(default_factory=lambda: os.getenv("PROXY_URL", ""))
    
    # ============================================
    # DELAYS (SEGUNDOS)
    # ============================================
    MIN_DELAY: float = field(default_factory=lambda: float(os.getenv("MIN_DELAY", "2.0")))
    MAX_DELAY: float = field(default_factory=lambda: float(os.getenv("MAX_DELAY", "5.0")))
    LONG_MIN_DELAY: float = 10.0
    LONG_MAX_DELAY: float = 20.0
    
    # ============================================
    # LIMITES DE AÇÕES
    # ============================================
    MAX_LIKES_PER_HOUR: int = field(default_factory=lambda: int(os.getenv("MAX_LIKES_PER_HOUR", "30")))
    MAX_FOLLOWS_PER_HOUR: int = field(default_factory=lambda: int(os.getenv("MAX_FOLLOWS_PER_HOUR", "20")))
    MAX_UNFOLLOWS_PER_HOUR: int = field(default_factory=lambda: int(os.getenv("MAX_UNFOLLOWS_PER_HOUR", "25")))
    MAX_COMMENTS_PER_HOUR: int = field(default_factory=lambda: int(os.getenv("MAX_COMMENTS_PER_HOUR", "8")))
    MAX_ACTIONS_PER_DAY: int = field(default_factory=lambda: int(os.getenv("MAX_ACTIONS_PER_DAY", "400")))
    
    # ============================================
    # CONTEÚDO
    # ============================================
    CONTENT_FOLDER: str = field(default_factory=lambda: os.getenv("CONTENT_FOLDER", "./content/images"))
    POSTS_PER_DAY: int = field(default_factory=lambda: int(os.getenv("POSTS_PER_DAY", "2")))
    DEFAULT_POST_HOURS: List[int] = field(default_factory=lambda: [int(h) for h in os.getenv("DEFAULT_POST_HOURS", "9,19").split(",")])
    
    # ============================================
    # ALVOS DE CRESCIMENTO
    # ============================================
    TARGET_HASHTAGS: List[str] = field(default_factory=lambda: os.getenv("TARGET_HASHTAGS", "tecnologia,programacao,developer").split(","))
    TARGET_INFLUENCERS: List[str] = field(default_factory=lambda: [u.strip() for u in os.getenv("TARGET_INFLUENCERS", "").split(",") if u.strip()])
    TARGET_COMPETITORS: List[str] = field(default_factory=lambda: [u.strip() for u in os.getenv("TARGET_COMPETITORS", "").split(",") if u.strip()])
    
    # ============================================
    # SELETORES DO INSTAGRAM (podem mudar!)
    # ============================================
    SELECTORS = {
        'username_input': 'input[name="username"]',
        'password_input': 'input[name="password"]',
        'login_button': 'button[type="submit"]',
        'like_button': 'svg[aria-label="Curtir"]',
        'unlike_button': 'svg[aria-label="Descurtir"]',
        'follow_button': '//button[contains(text(), "Seguir") and not(contains(text(), "Seguindo"))]',
        'following_button': '//button[contains(text(), "Seguindo")]',
        'comment_input': 'textarea[aria-label="Adicione um comentário..."]',
        'post_links': 'a[href*="/p/"]',
        'not_now_button': '//button[contains(text(), "Agora não")]',
        'save_info_button': '//button[contains(text(), "Salvar informações")]',
        'create_post_button': 'svg[aria-label="Nova publicação"]',
        'story_ring': 'div._aarf',
        'likes_link': "//a[contains(@href, '/liked_by')]",
        'followers_link': "//a[contains(@href, '/followers')]",
        'following_link': "//a[contains(@href, '/following')]",
        'dialog_container': "div[role='dialog'] div._aano",
    }
    
    # ============================================
    # ARQUIVOS DE DADOS
    # ============================================
    DATA_DIR: str = "./data"
    LOGS_DIR: str = "./logs"
    COOKIES_FILE: str = "./data/session_cookies.pkl"
    
    # ============================================
    # DEBUG
    # ============================================
    DEBUG_MODE: bool = field(default_factory=lambda: os.getenv("DEBUG_MODE", "False").lower() == "true")
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if not self.IG_USERNAME or not self.IG_PASSWORD:
            print("⚠️  AVISO: Credenciais não configuradas!")
            print("   Configure IG_USERNAME e IG_PASSWORD no arquivo .env")
        
        # Cria diretórios necessários
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        os.makedirs(self.CONTENT_FOLDER, exist_ok=True)

# Instância global
config = Config()
