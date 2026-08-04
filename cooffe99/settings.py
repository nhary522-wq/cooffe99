
import os
from pathlib import Path

from dotenv import load_dotenv


# =============================================================================
# المسار الأساسي للمشروع
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# تحميل متغيرات البيئة
# =============================================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# =============================================================================
# دوال مساعدة لقراءة متغيرات البيئة
# =============================================================================

def get_env_bool(name: str, default: bool = False) -> bool:
    """
    تحويل متغير البيئة إلى قيمة منطقية.

    القيم التي تُعتبر True:
    1, true, yes, on
    """

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_env_list(name: str, default: str = "") -> list[str]:
    """
    تحويل متغير بيئة مفصول بفواصل إلى قائمة.
    """

    value = os.getenv(name, default)

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def get_required_env(name: str) -> str:
    """
    قراءة متغير بيئة إجباري.

    يظهر خطأ واضح إذا كان المتغير غير موجود أو فارغًا.
    """

    value = os.getenv(name, "").strip()

    if not value:
        raise RuntimeError(
            f"متغير البيئة الإجباري {name} غير موجود أو فارغ."
        )

    return value


# =============================================================================
# تحديد بيئة التشغيل
# =============================================================================

DATABASE_MODE = os.getenv(
    "DATABASE_MODE",
    "development",
).strip().lower()

IS_PRODUCTION = DATABASE_MODE == "production"
RENDER_EXTERNAL_HOSTNAME = os.getenv(
    "RENDER_EXTERNAL_HOSTNAME",
    "",
).strip()
IS_RENDER = bool(RENDER_EXTERNAL_HOSTNAME)


# =============================================================================
# إعدادات الأمان الأساسية
# =============================================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-key-change-this",
)

DEBUG = get_env_bool(
    "DJANGO_DEBUG",
    default=not (IS_PRODUCTION or IS_RENDER),
)

if IS_RENDER:
    DEBUG = False

ALLOWED_HOSTS = get_env_list(
    "DJANGO_ALLOWED_HOSTS",
    default="127.0.0.1,localhost,cooffe99.onrender.com",
)

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = get_env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default="https://cooffe99.onrender.com",
)

if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{RENDER_EXTERNAL_HOSTNAME}"
    )

# منع تشغيل الإنتاج بمفتاح Django الافتراضي
if IS_PRODUCTION:
    if SECRET_KEY == "django-insecure-development-key-change-this":
        raise RuntimeError(
            "يجب تعيين DJANGO_SECRET_KEY آمن في بيئة الإنتاج."
        )

# =============================================================================
# التطبيقات المثبتة
# =============================================================================

INSTALLED_APPS = [
    # تطبيقات Django الأساسية
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Cloudinary
    "cloudinary_storage",
    "cloudinary",

    # Django Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.apple",

    # تطبيقات المشروع
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "catalog.apps.CatalogConfig",
    "orders.apps.OrdersConfig",
    "payments.apps.PaymentsConfig",
    "dashboard.apps.DashboardConfig",
]


# =============================================================================
# البرامج الوسيطة
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.locale.LocaleMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "allauth.account.middleware.AccountMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =============================================================================
# ملف الروابط الرئيسي
# =============================================================================

ROOT_URLCONF = "cooffe99.urls"


# =============================================================================
# إعدادات القوالب
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth."
                    "context_processors.auth"
                ),
                (
                    "django.contrib.messages."
                    "context_processors.messages"
                ),
                "core.context_processors.cart_summary",
            ],
        },
    },
]


# =============================================================================
# إعدادات WSGI
# =============================================================================

WSGI_APPLICATION = "cooffe99.wsgi.application"


# =============================================================================
# إعدادات قاعدة البيانات
# =============================================================================

if IS_PRODUCTION:
    # -------------------------------------------------------------------------
    # قاعدة بيانات PostgreSQL الخاصة بالإنتاج
    # -------------------------------------------------------------------------

    database_options = {}

    database_sslmode = os.getenv(
        "DB_SSLMODE",
        "",
    ).strip()

    if database_sslmode:
        database_options["sslmode"] = database_sslmode

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",

            "NAME": get_required_env(
                "DB_NAME",
            ),

            "USER": get_required_env(
                "DB_USER",
            ),

            "PASSWORD": get_required_env(
                "DB_PASSWORD",
            ),

            "HOST": get_required_env(
                "DB_HOST",
            ),

            "PORT": os.getenv(
                "DB_PORT",
                "5432",
            ),

            # إبقاء الاتصال مفتوحًا لفترة لتحسين الأداء
            "CONN_MAX_AGE": int(
                os.getenv(
                    "DB_CONN_MAX_AGE",
                    "60",
                )
            ),

            # التأكد من صلاحية الاتصال قبل استعماله
            "CONN_HEALTH_CHECKS": True,

            "OPTIONS": database_options,
        }
    }

else:
    # -------------------------------------------------------------------------
    # قاعدة SQLite المحلية الخاصة بالتطوير
    # -------------------------------------------------------------------------

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",

            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =============================================================================
# نموذج المستخدم المخصص
# =============================================================================

# فعّل هذا السطر فقط إذا كان لديك نموذج User مخصص داخل accounts.
# يجب أن يكون اسم الكلاس فعلًا User.
#
# AUTH_USER_MODEL = "accounts.User"


# =============================================================================
# التحقق من كلمات المرور
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =============================================================================
# اللغة والمنطقة الزمنية
# =============================================================================

LANGUAGE_CODE = "ar"

TIME_ZONE = "Asia/Riyadh"

USE_I18N = True

USE_TZ = True


# =============================================================================
# الملفات الثابتة Static Files
# =============================================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# =============================================================================
# إعدادات Cloudinary
# =============================================================================

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv(
        "CLOUDINARY_CLOUD_NAME",
        "",
    ),

    "API_KEY": os.getenv(
        "CLOUDINARY_API_KEY",
        "",
    ),

    "API_SECRET": os.getenv(
        "CLOUDINARY_API_SECRET",
        "",
    ),

    "SECURE": True,
}


# =============================================================================
# ملفات الوسائط Media Files
# =============================================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =============================================================================
# إعدادات التخزين
# =============================================================================

STORAGES = {
    # رفع الصور والوسائط إلى Cloudinary
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage."
            "MediaCloudinaryStorage"
        ),
    },

    # إبقاء static بالطريقة الافتراضية
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# =============================================================================
# إعدادات تسجيل الدخول والخروج
# =============================================================================

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/"


# =============================================================================
# إعدادات الجلسات والكوكيز
# =============================================================================

SESSION_COOKIE_SECURE = IS_PRODUCTION

CSRF_COOKIE_SECURE = IS_PRODUCTION

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"


# =============================================================================
# إعدادات HTTPS في الإنتاج
# =============================================================================

SECURE_SSL_REDIRECT = get_env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    default=IS_PRODUCTION,
)

SECURE_HSTS_SECONDS = int(
    os.getenv(
        "DJANGO_SECURE_HSTS_SECONDS",
        "31536000" if IS_PRODUCTION else "0",
    )
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION

SECURE_HSTS_PRELOAD = IS_PRODUCTION

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"


# مهم عند تشغيل Django خلف Render أو أي Reverse Proxy
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


# =============================================================================
# المفتاح الأساسي الافتراضي
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# مساعد A23 الذكي
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.6-terra").strip()


# =============================================================================
# خلفيات المصادقة
# =============================================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",

    (
        "allauth.account.auth_backends."
        "AuthenticationBackend"
    ),
]


# =============================================================================
# إعدادات Django Allauth
# =============================================================================

ACCOUNT_LOGIN_METHODS = {
    "email",
}

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "password1*",
    "password2*",
]

SOCIALACCOUNT_LOGIN_ON_GET = True


# =============================================================================
# إعدادات تسجيل الدخول بواسطة Google وApple
# =============================================================================

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv(
                "GOOGLE_CLIENT_ID",
                "",
            ),

            "secret": os.getenv(
                "GOOGLE_CLIENT_SECRET",
                "",
            ),

            "key": "",
        },

        "SCOPE": [
            "profile",
            "email",
        ],

        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },

    "apple": {
        "APP": {
            "client_id": os.getenv(
                "APPLE_CLIENT_ID",
                "",
            ),

            "secret": os.getenv(
                "APPLE_CLIENT_SECRET",
                "",
            ),

            "key": os.getenv(
                "APPLE_KEY_ID",
                "",
            ),

            "settings": {
                "certificate_key": os.getenv(
                    "APPLE_PRIVATE_KEY",
                    "",
                ),
            },
        },
    },
}


# =============================================================================
# إعدادات البريد الإلكتروني
# =============================================================================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_USE_TLS = get_env_bool(
    "EMAIL_USE_TLS",
    default=True,
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER,
)

