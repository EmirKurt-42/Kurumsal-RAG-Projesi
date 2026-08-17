# ---------------------------------------------------------------------------
# Geliştirme komutları. Her hedef iki servise de uygulanır.
# ---------------------------------------------------------------------------
SERVICES := services/user_service services/order_service
PYTHON   ?= python3

.PHONY: install run-user run-order test lint format clean

install:  ## Her servisi kendi bağımlılıklarıyla, düzenlenebilir modda kurar
	@for s in $(SERVICES); do \
		echo "==> installing $$s"; \
		$(PYTHON) -m pip install -e "$$s[dev]"; \
	done

run-user:  ## user_service'i 8001 portunda başlatır
	cd services/user_service && $(PYTHON) -m uvicorn user_service.main:app --reload --port 8001

run-order:  ## order_service'i 8002 portunda başlatır
	cd services/order_service && $(PYTHON) -m uvicorn order_service.main:app --reload --port 8002

test:  ## Tüm servislerin testlerini koşar
	@for s in $(SERVICES); do \
		echo "==> testing $$s"; \
		(cd $$s && $(PYTHON) -m pytest) || exit 1; \
	done

lint:  ## Stil (ruff) ve tip (mypy) kontrolleri
	@for s in $(SERVICES); do \
		echo "==> linting $$s"; \
		(cd $$s && $(PYTHON) -m ruff check src tests && $(PYTHON) -m mypy src) || exit 1; \
	done

format:  ## Kodu otomatik biçimlendirir
	@for s in $(SERVICES); do \
		(cd $$s && $(PYTHON) -m ruff format src tests && $(PYTHON) -m ruff check --fix src tests); \
	done

clean:  ## Geçici dosyaları temizler
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache -o -name '*.egg-info' \) -exec rm -rf {} +
	find . -name '*.db' -delete
