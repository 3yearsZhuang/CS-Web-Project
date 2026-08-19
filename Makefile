# ============ FztbuCS-Project 根级命令入口 ============
# 统一管理本地开发（并行起前后端）与容器化部署（全栈 compose）。
#
# 常用命令：
#   make dev-up       并行起本地前后端（后台进程，不依赖 tmux，:9000 + :2333）
#   make dev-backend  仅起后端
#   make dev-frontend 仅起前端
#   make dev-logs     跟踪前后端日志（tail -f，Ctrl+C 退出）
#   make dev-down     按 PID 精准关停前后端（读 .dev.pid）
#   make setup        首次：复制 .env.example → .env
#   make up           全栈 Docker 部署（db+backend+redis+worker+frontend；前端绑定 127.0.0.1:2333）
#   make down / logs / ps / rebuild
#   make check        跑全部自检（契约+文档+前端边界+版本），亦可 make check-contract / check-docs / check-fe-boundary / check-version-group 单跑
#
# 前置：根目录已 git init 并将前后端作为 submodule 收敛（方案②）。
#
# 本地开发说明：
#   - 本地 dev 用后台进程（nohup）替代 tmux，开箱即用，无需额外安装 tmux。
#     前后端 PID 写入根级 .dev.pid，日志分别落盘 .dev-backend.log / .dev-frontend.log。
#   - 后端用 CS-Web-Backend/.venv（Python 3.13+）。系统 python 可能不存在或版本过低，
#     故统一走 venv 内解释器，避免 `python: command not found` / 版本不兼容。
#   - 后端本地开发直连本机 PostgreSQL（.env.development 中 DATABASE_HOST=localhost:5432）。

# 后端 venv 解释器（如未创建 venv，先 `cd CS-Web-Backend && uv venv` 或用你的方式建 venv）
# 用绝对路径，避免 `cd CS-Web-Backend` 后相对路径失效。
BACKEND_PY := $(CURDIR)/CS-Web-Backend/.venv/bin/python
BACKEND_PORT := 9000
FRONTEND_PORT := 2333

.PHONY: dev-up dev-backend dev-frontend dev-logs dev-down restart-frontend setup up down logs ps rebuild status contract-baseline contract-check check-version check check-contract check-docs check-fe-boundary check-version-group check-gitignore-sync deps-export clean-artifacts

# 本地开发统一用后台进程托管（不依赖 tmux，开箱即用）。
# 前后端各自 nohup 后台运行，PID 写入 .dev.pid，日志落盘 .dev-*.log。
DEV_PID := $(CURDIR)/.dev.pid
DEV_BACKEND_LOG := $(CURDIR)/.dev-backend.log
DEV_FRONTEND_LOG := $(CURDIR)/.dev-frontend.log

# ---- 本地开发 ----
# 用后台进程并行托管前后端（无需 tmux）：
#   backend :9000 热重载、frontend :2333 dev。
# PID 写入 .dev.pid，dev-down 按 PID 精准关停（不误杀同名进程）。
# 看实时日志：make dev-logs（tail -f 合并看两个日志）。
dev-up:
	@if [ -f $(DEV_PID) ]; then \
		echo ">>> 已在运行（或残留 $(DEV_PID)），先 make dev-down 再起"; exit 1; \
	fi
	@echo ">>> 启动后端 (:$(BACKEND_PORT)) ..."
	@cd $(CURDIR)/CS-Web-Backend && nohup $(BACKEND_PY) run.py --env 1 --port $(BACKEND_PORT) > $(DEV_BACKEND_LOG) 2>&1 & echo $$! > $(DEV_PID)
	@echo ">>> 启动前端 (:$(FRONTEND_PORT)) ..."
	@cd $(CURDIR)/CS-Web-Frontend && nohup pnpm dev > $(DEV_FRONTEND_LOG) 2>&1 & echo $$! >> $(DEV_PID)
	@echo ""
	@echo ">>> 本地全栈已在后台启动："
	@echo "    前端 http://localhost:$(FRONTEND_PORT)   后端 http://localhost:$(BACKEND_PORT)"
	@echo "    看日志：make dev-logs    停止：make dev-down"

# 仅起后端（后台进程；若 .dev.pid 已存在则追加，否则新建）
dev-backend:
	@cd $(CURDIR)/CS-Web-Backend && nohup $(BACKEND_PY) run.py --env 1 --port $(BACKEND_PORT) > $(DEV_BACKEND_LOG) 2>&1 & echo $$! >> $(DEV_PID)
	@echo ">>> 后端已在后台启动（:$(BACKEND_PORT)，日志 $(DEV_BACKEND_LOG)）"

# 仅起前端（后台进程；若 .dev.pid 已存在则追加，否则新建）
dev-frontend:
	@cd $(CURDIR)/CS-Web-Frontend && nohup pnpm dev > $(DEV_FRONTEND_LOG) 2>&1 & echo $$! >> $(DEV_PID)
	@echo ">>> 前端已在后台启动（:$(FRONTEND_PORT)，日志 $(DEV_FRONTEND_LOG)）"

# 跟踪前后端日志（Ctrl+C 退出 tail，不杀进程）
dev-logs:
	@tail -f $(DEV_BACKEND_LOG) $(DEV_FRONTEND_LOG)

# 按 .dev.pid 关停前后端，并递归杀进程树 + 按端口兜底清理，避免 worker 子进程残留占端口。
dev-down:
	@if [ -f $(DEV_PID) ]; then \
		while read pid; do \
			pkill -P $$pid 2>/dev/null; \
			kill $$pid 2>/dev/null && echo "已停止 PID $$pid" || echo "PID $$pid 已不存在"; \
		done < $(DEV_PID); \
		rm -f $(DEV_PID); \
	else echo "无 $(DEV_PID)，进程可能已停或从未用 make dev-up 启动"; fi
	@# 兜底：清理仍占用端口的残留进程（父进程被杀后 fork 出的孤儿 worker）
	@for p in $(BACKEND_PORT) $(FRONTEND_PORT); do \
		pids=$$(lsof -nP -iTCP:$$p -sTCP:LISTEN -t 2>/dev/null); \
		if [ -n "$$pids" ]; then \
			echo ">>> 端口 $$p 仍有残留进程 $$pids，强制清理"; \
			echo "$$pids" | xargs -r kill -9 2>/dev/null; \
		fi; \
	done
	@echo ">>> dev-down 完成"

# 前端 BFF 路由（活动/社区/登录）全部 500、静态页却正常时，多为 tsx watch 热重载
# 缓存损坏（如大规模删代码后）。无需改代码，冷重启 dev server 即可恢复。
restart-frontend:
	@echo ">>> 冷重启前端 dev server（释放 :2333 并重新 pnpm dev）..."
	cd CS-Web-Frontend && node ./tools/scripts/fe/build/restart-frontend.mjs

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

# ---- 自检聚合入口（按功能分组）----
# make check              跑全部自检（契约 + 文档 + 前端边界 + 版本 + gitignore）
# make check-contract     仅契约比对（基线更新走显式 make contract-baseline）
# make check-docs         仅文档死链
# make check-fe-boundary  仅 BFF 安全边界
# make check-version-group 仅版本四源一致
# make check-gitignore-sync 仅 .gitignore 公共段一致性
# 下列原子目标（contract-baseline 等）保留为别名，CI / 旧习惯仍可调用。
check: check-contract check-docs check-fe-boundary check-version-group check-gitignore-sync
	@echo ">>> 全部自检通过 ✅"

# 契约类（G3：API 契约冻结）
check-contract: contract-check

# 文档类（ER-09：死链审计）
check-docs: check-docs-links

# 前端边界类（AL-1：BFF 安全边界）
check-fe-boundary: check-bff-boundary

# 版本类（ER-33：版本四源一致）
check-version-group: check-version

# ---- API 契约冻结（G3）----
# 生成基线（评审通过后执行，会覆盖仓库根 openapi.baseline.json）：
# 注意：须用后端 venv（Python 3.13+）。如未激活，可改为 CS-Web-Backend/.venv/bin/python。
contract-baseline:
	cd CS-Web-Backend && (.venv/bin/python tools/scripts/contract/export_openapi.py --baseline openapi.baseline.json || python tools/scripts/contract/export_openapi.py --baseline openapi.baseline.json)
	mv CS-Web-Backend/openapi.baseline.json openapi.baseline.json
# 比对当前契约与基线（CI 门禁，差异即失败）：
contract-check:
	cd CS-Web-Backend && (.venv/bin/python tools/scripts/contract/export_openapi.py --check ../openapi.baseline.json || python tools/scripts/contract/export_openapi.py --check ../openapi.baseline.json)
# 生成 API 参考文档（ReDoc 查看器，D1：由基线真实生成，勿手改；需网络拉取 npx 包）：
gen-api-docs:
	npx -y @redocly/cli@latest build-docs openapi.baseline.json -o docs/api-reference.html

# ---- 文档死链审计（ER-09）----
# 可复现的 PR 门禁：扫描 docs/ 与根级 *.md，断文件链接即失败。
# 锚点默认仅警告；--strict-anchors 时缺失锚点也计为错误。
check-docs-links:
	python3 scripts/check/check_dead_links.py --base . --docs docs

# ---- .gitignore 公共段一致性（C-8 / N-04）----
check-gitignore-sync:
	python3 scripts/check/check_gitignore_sync.py

# ---- BFF 安全边界（AL-1）----
# 前端边界门禁：'use client' 文件禁止从 @/shared/security（非 schemas 子树）导入权威安全模块
# （密码哈希/权限判定/JWT 签发等），后端为认证/授权唯一权威。
check-bff-boundary:
	cd CS-Web-Frontend && pnpm run check:bff-boundary

# ---- 版本四源一致校验（ER-33）----
# 校验 pyproject / __init__ / package.json / uv.lock 四处版本号一致，不一致即失败。
check-version:
	python3 scripts/check/check_version_sync.py

# ---- 依赖锁生成（C-7/A'：uv 单源，2026-08-17）----
# 依赖唯一来源为 CS-Web-Backend/pyproject.toml；改依赖后执行本目标：
#   uv lock 重算 uv.lock → uv export 重生成 requirements.lock / requirements-dev.lock。
# （CI / Docker / Jenkins 继续消费这两个带哈希的锁，安装逻辑不变；uv export 默认含 --hash）
deps-export:
	cd CS-Web-Backend && uv lock && \
	uv export --format requirements-txt -o requirements.lock && \
	uv export --extra dev --format requirements-txt -o requirements-dev.lock
	@echo ">>> 依赖锁已重生成（uv.lock / requirements.lock / requirements-dev.lock）"

# ---- 清理构建可再生产物与确定无用文件（A+B，安全：跳过被 git 跟踪的源码）----
#   make clean-artifacts                  # 预览（dry-run），复核将要删除的目标
#   make clean-artifacts APPLY=1          # 真删（A+B：.build / 缓存 / 日志 / 临时）
#   make clean-artifacts APPLY=1 WITH_DEPS=1  # 含依赖 node_modules/.venv（C）
# 安全守卫：凡 git 跟踪的路径（如 tools/scripts/fe/build 源码）一律跳过，绝不误删。
clean-artifacts:
	@bash $(CURDIR)/scripts/clean-artifacts.sh $(if $(filter 1,$(APPLY)),--apply,) $(if $(filter 1,$(WITH_DEPS)),--with-deps,)
	@echo ">>> clean-artifacts 完成（默认 dry-run，确认无误后 APPLY=1 真删）"

