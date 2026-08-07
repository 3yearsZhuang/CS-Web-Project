# ============ FztbuCS-Project 根级命令入口 ============
# 统一管理本地开发（并行起前后端）与容器化部署（全栈 compose）。
#
# 常用命令：
#   make dev-up       并行起本地前后端（tmux 会话托管，:9000 + :2333）
#   make dev-backend  仅起后端
#   make dev-frontend 仅起前端
#   make dev-logs     进入 tmux 会话实时看前后端日志（Ctrl+B 再 D 脱离）
#   make dev-down     一键关停整个 dev 会话（前后端一起停）
#   make setup        首次：复制 .env.example → .env
#   make up           全栈 Docker 部署（外部 PostgreSQL+外部 Redis+backend+worker+frontend；前端绑定 127.0.0.1:2333）
#   make down / logs / ps / rebuild
#
# 前置：根目录已 git init 并将前后端作为 submodule 收敛（方案②）。
#
# 本地开发依赖：
#   - 后端用 CS-Web-Backend/.venv（Python 3.13+）。系统 python 可能不存在或版本过低，
#     故统一走 venv 内解释器，避免 `python: command not found` / 版本不兼容。
#   - 后端本地开发直连本机 PostgreSQL（.env.development 中 DATABASE_HOST=localhost:5432）。

# 后端 venv 解释器（如未创建 venv，先 `cd CS-Web-Backend && uv venv` 或用你的方式建 venv）
# 用绝对路径，避免 `cd CS-Web-Backend` 后相对路径失效。
BACKEND_PY := $(CURDIR)/CS-Web-Backend/.venv/bin/python
BACKEND_PORT := 9000
FRONTEND_PORT := 2333

.PHONY: dev-up dev-backend dev-frontend dev-logs dev-down restart-frontend setup up down logs ps rebuild status contract-baseline contract-check

# 本地开发统一用 tmux 会话托管（会话名固定，便于一键停/看日志）。
# 会话内两个窗口：backend（:9000 热重载）、frontend（:2333 dev）。
DEV_SESSION := cs-dev

# ---- 本地开发 ----
# 用 tmux 会话统一托管前后端：两个窗口 backend / frontend 并行运行，
# `make dev-down` 一键关掉整个会话（前后端一起停，不残留 detached 进程）。
# 看实时日志：`make dev-logs`（进入会话，Ctrl+B 再按 D 脱离）。
dev-up:
	@if tmux has-session -t $(DEV_SESSION) 2>/dev/null; then \
		echo ">>> 会话 $(DEV_SESSION) 已存在，先 make dev-down 再起"; exit 1; \
	fi
	@echo ">>> 创建 tmux 会话 $(DEV_SESSION) 并行启动前后端..."
	@tmux new-session -d -s $(DEV_SESSION) -n backend
	@tmux send-keys -t $(DEV_SESSION):backend "cd $(CURDIR)/CS-Web-Backend && $(BACKEND_PY) run.py --env 1 --port $(BACKEND_PORT)" C-m
	@tmux new-window -t $(DEV_SESSION) -n frontend
	@tmux send-keys -t $(DEV_SESSION):frontend "cd $(CURDIR)/CS-Web-Frontend && pnpm dev" C-m
	@tmux select-window -t $(DEV_SESSION):backend
	@echo ""
	@echo ">>> 本地全栈已在 tmux 会话 $(DEV_SESSION) 中并行启动："
	@echo "    前端 http://localhost:$(FRONTEND_PORT)   后端 http://localhost:$(BACKEND_PORT)"
	@echo "    看日志：make dev-logs    停止：make dev-down"

# 仅起后端（独立 tmux 窗口，若会话不存在则新建）
dev-backend:
	@tmux has-session -t $(DEV_SESSION) 2>/dev/null || tmux new-session -d -s $(DEV_SESSION) -n backend
	@tmux new-window -t $(DEV_SESSION) -n backend 2>/dev/null || true
	@tmux send-keys -t $(DEV_SESSION):backend "cd $(CURDIR)/CS-Web-Backend && $(BACKEND_PY) run.py --env 1 --port $(BACKEND_PORT)" C-m
	@echo ">>> 后端已在 $(DEV_SESSION):backend 启动（:$(BACKEND_PORT)）"

# 仅起前端（独立 tmux 窗口，若会话不存在则新建）
dev-frontend:
	@tmux has-session -t $(DEV_SESSION) 2>/dev/null || tmux new-session -d -s $(DEV_SESSION) -n frontend
	@tmux new-window -t $(DEV_SESSION) -n frontend 2>/dev/null || true
	@tmux send-keys -t $(DEV_SESSION):frontend "cd $(CURDIR)/CS-Web-Frontend && pnpm dev" C-m
	@echo ">>> 前端已在 $(DEV_SESSION):frontend 启动（:$(FRONTEND_PORT)）"

# 进入 tmux 会话实时看前后端日志（Ctrl+B 再按 D 脱离，不杀进程）
dev-logs:
	@tmux attach-session -t $(DEV_SESSION)

# 一键关停整个 dev 会话（前后端一起停）
dev-down:
	@echo ">>> 停止本地 dev 会话（前后端一起关停）..."
	@tmux kill-session -t $(DEV_SESSION) 2>/dev/null && echo "已关闭会话 $(DEV_SESSION)" || echo "无运行中的 $(DEV_SESSION) 会话"

# 前端 BFF 路由（活动/社区/登录）全部 500、静态页却正常时，多为 tsx watch 热重载
# 缓存损坏（如大规模删代码后）。无需改代码，冷重启 dev server 即可恢复。
restart-frontend:
	@echo ">>> 冷重启前端 dev server（释放 :2333 并重新 pnpm dev）..."
	cd CS-Web-Frontend && node ./tools/scripts/restart-frontend.mjs

# ---- 容器化部署（根级全栈 compose）----

setup:
	@test -f .env || { cp .env.example .env && echo "已生成 .env，请填写密钥后继续"; }
	@echo ">>> 请编辑 .env 填写 DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

rebuild:
	docker compose up -d --build --force-recreate

status:
	git submodule status
	git status --short

# ---- API 契约冻结（G3）----
# 生成基线（评审通过后执行，会覆盖仓库根 openapi.baseline.json）：
# 注意：须用后端 venv（Python 3.13+）。如未激活，可改为 CS-Web-Backend/.venv/bin/python。
contract-baseline:
	cd CS-Web-Backend && (.venv/bin/python tools/scripts/export_openapi.py --baseline openapi.baseline.json || python tools/scripts/export_openapi.py --baseline openapi.baseline.json)
	mv CS-Web-Backend/openapi.baseline.json openapi.baseline.json
# 比对当前契约与基线（CI 门禁，差异即失败）：
contract-check:
	cd CS-Web-Backend && (.venv/bin/python tools/scripts/export_openapi.py --check ../openapi.baseline.json || python tools/scripts/export_openapi.py --check ../openapi.baseline.json)
