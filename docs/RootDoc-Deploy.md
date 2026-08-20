# RootDoc-Deploy：全栈部署 How-to（7 个目标场景 · 一步一结果）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.1 · 七夕（子模块指针 cfa270a / 884f68a / ceb1f9b；版本三源同步：pyproject / __init__.py / package.json）
> Diátaxis：H（How-to · 目标导向 · 每个场景解决一个具体部署/运维问题；不教原理，只给可复制的命令序列与验收标准）
> 适用读者：已完成 Onboarding 的部署管理员、负责发布/回滚/迁移的 release owner、生产环境 SRE；不适合第一次接触项目的新人（新人先做 [Onboarding.md](Onboarding.md) Tutorial）
> 变更触发：新增/调整 Makefile 部署入口 / docker compose 服务拓扑 / 健康检查端点 / 备份恢复脚本 / SLO 目标 / 外部反向代理接入方式 / CI 分工或门禁

> **SSOT 分工声明（避免 Double-source）**：
> - 本文档是「**根级编排层部署 7 个目标场景**」的唯一权威（docker compose 拓扑 / 备份恢复 / 回滚 / SLO / CI 分工）。
> - 端侧专项运维 Runbook：后端（运维端点深度解释、OTel、迁移验证）权威 → [BackDoc-Infra.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-Infra.md)；前端（Docker 细节、外部反向代理配置模板、端点级 SLO 预算消耗评审流程）权威 → `CS-Web-Frontend/tools/docs/FrontDoc-Ops.md`。
> - 实现级约束（MUST/MUST NOT 的原理与边界）→ [RootDoc-EngConv.md](RootDoc-EngConv.md) 与三仓 `-02-Sec.md`。
> - 学习导向的环境搭建流程 → [Onboarding.md](Onboarding.md) §0–§6（与本文 §A / §B 场景对齐，但受众不同）。
> - 移动端部署（小程序提审 / APK 签名加固）权威 → [MobileDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-03-Conv.md) §5，本文不重复。

> **前置条件（全部满足后才能进入任何场景）**：
> 1. 已读完本文档末尾「§S. 成功标准总表」，知道每个场景最终要达到什么结果、用哪条命令验收。
> 2. 本机/服务器：Docker + Compose v2、Node ≥ 22、Python ≥ 3.13、端口 2333 / 8000 / 5432 / 6379 空闲。
> 3. 有 `DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET` 四条密钥（本地或生产各一份；生产与本地 MUST 不同）。
> 4. 生产部署 MUST 已准备好 HTTPS 外部反向代理（nginx / traefik / caddy 任一）；本文不教怎么装反代，但会给出转发规则。

---

## 本文 7 个目标场景（选择你要完成的一个，直接跳到对应节）

| # | 场景名称（H 类目标导向） | 适用时机 | 读一节约需 |
|---|---|---|---|
| **A** | **首次本地开发启动（make dev-up 前后端并行）** | 刚拉完代码、Onboarding §4 | 3 min |
| **B** | **容器化全栈生产部署（make up → HTTPS 反代接入）** | 部署到 staging / prod 服务器 | 8 min |
| **C** | **健康检查 + 运维端点验收（6 条端点 + 探针配置）** | 部署后确认可观测性健全 | 4 min |
| **D** | **数据备份 + 异地传输（每日 cron / 手动导出）** | 每日例行、迁移前必做 | 3 min |
| **E** | **从备份恢复 + 开发库→生产库迁移（PG→PG）** | 故障恢复 / 首次上线数据迁移 | 8 min |
| **F** | **版本升级回滚（代码 + Alembic 迁移 双向）** | 发版失败时 10 分钟止损 | 4 min |
| **G** | **SLO 对齐 + 可观测性最小集 + 巡检日历** | SRE 接岗 / 生产稳定期 | 6 min |

> **How-to 阅读规则**：不必从头读到尾，挑你当下要达成的那个目标场景按编号跳。每节内「步骤」= 可复制的命令；「成功标准」= 本节做完后 MUST 全部通过的验收。未达成功标准 → 跳本节末尾的「失败回退路径」。

---

## 场景 A：首次本地开发启动（目标：浏览器 2333 打开登录页）

**适用**：刚 clone 完仓库、填完本地 `.env`（Onboarding §2–§3 已完成）。

### A.1 操作步骤（2 条命令）

```bash
# 根目录执行
make setup         # 首次：cp .env.example .env；若已有 .env 跳过
make dev-up        # 前台并行：后端 run.py --port 9000（热重载）+ 前端 pnpm dev（:2333）
```

等待两条就绪日志：
- 后端：`Uvicorn running on http://0.0.0.0:9000` + `Application startup complete`
- 前端：`ready started server on 0.0.0.0:2333`

### A.2 成功标准（3 条 curl 全过）

新开终端：

```bash
curl -s http://localhost:9000/health          # A.2-1 → {"status":"ok"}
curl -s http://localhost:2333/api/health      # A.2-2 → {"status":"ok"}  （BFF 转发链通）
curl -s -o /dev/null -w "%{http_code}" http://localhost:2333/login   # A.2-3 → 200
```

三条全部满足 → 场景 A 成功；接下来浏览器打开 http://localhost:2333 继续 Onboarding §5。

### A.3 失败回退路径（按优先级排查）

| 症状 | 处理 |
|---|---|
| A.2-1 失败（后端直连不通） | `docker compose ps` 看 db/redis 是否 Up healthy；后端日志末尾 50 行 `docker compose logs backend --tail 50`（若 db 起了但后端未起） |
| A.2-2 失败（BFF 转发 500） | 前端 `.env` 的 `BACKEND_URL=http://localhost:9000`；`AUTH_SESSION_SECRET` 与后端一致；冷重启前端：`make restart-frontend` |
| 任何一方报端口占用 | 第 0.2 步 Onboarding.md `lsof -i :<port>` 找 PID；或 [Onboarding.md](Onboarding.md) §8.1 替代端口表 |

---

## 场景 B：容器化全栈生产部署（目标：HTTPS 域名访问 + 全站 200）

**适用**：将 1.0.x 部署到 staging 或生产服务器；外部反代 + HTTPS 已就位（未就绪前 MUST 只绑定回环地址）。

### B.1 拓扑速览（部署后端口暴露）

```
公网 HTTPS（443）──→ 外部反代（nginx/traefik/caddy）──→ 127.0.0.1:2333  cs-website（Next.js BFF）
                                                       │ BACKEND_URL=http://backend:8000（容器内网 cs-net）
                                                       ▼
                                                 backend（FastAPI，expose:8000，不映射宿主机）──→ db（PG 5432）+ redis（6379）
```

关键不变量：
- 后端容器 **MUST NOT** 映射宿主机端口；只靠前端 BFF 经内网 `backend:8000` 直连。
- 前端容器端口映射 **MUST** 默认 `127.0.0.1:2333:3000`；禁止 `0.0.0.0` 裸暴露（HTTPS 走反代）。

### B.2 操作步骤（6 步）

```bash
# B.2-1 拷贝环境模板
make setup        # 生成根级 .env（docker compose 读这个）

# B.2-2 填写根级 .env 的 4 个必填 + 3 个生产必填
#  4 条密钥：DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET
#  3 条生产必填：
#    ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
#    NEXT_PUBLIC_SITE_URL=https://your-domain.com
#    TRUST_PROXY=true
#  （可选）LLM_* 项按 RootDoc-EngConv §4 的矩阵启用；默认 none 不影响部署

# B.2-3 一键全栈起（首次 build 需要 5–15 分钟下载基础镜像）
make up           # = docker compose up -d --build（db + backend + redis + worker + frontend 全部）

# B.2-4 本机服务器验证（确认容器内链路通，此时还没配反代）
curl -s http://127.0.0.1:2333/api/health     # B.2-4a → {"status":"ok"}
curl -s http://127.0.0.1:2333/login | head -5 # B.2-4b → 返回 HTML（200）

# B.2-5 接入外部反向代理。以下为 nginx 最小配置片段（仅示意；Apache/traefik 等价）
cat > /etc/nginx/conf.d/fztbucs.conf <<'NGINX'
server {
  listen 443 ssl http2;
  server_name your-domain.com www.your-domain.com;

  # TLS：certbot 或上传自有证书；MUST HSTS 启用
  ssl_certificate     /etc/letsencrypt/live/your-domain.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;

  # 反代到前端 BFF（容器宿主机回环）
  location / {
    proxy_pass http://127.0.0.1:2333;
    proxy_http_version 1.1;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;   # 让 TRUST_PROXY=true 正确识别 secure cookie
    proxy_read_timeout 60s;
    proxy_send_timeout 60s;
  }

  # 大文件上传（头像/社区图）；默认 client_max_body_size 1m 太小会 413
  client_max_body_size 50m;
}
NGINX
nginx -t && systemctl reload nginx

# B.2-6 HTTPS 公网验证（从你本地电脑或外部 VPS 发；不要在服务器内 curl）
curl -sI https://your-domain.com/              # B.2-6a → HTTP/2 200；含 Strict-Transport-Security 头
curl -sI https://your-domain.com/api/health    # B.2-6b → HTTP/2 200
```

### B.3 成功标准（5 条）

- B.2-4a/b 在服务器本机全 200；
- B.2-6a/b 外网 HTTPS 全 200 + HSTS 头出现；
- `make ps` 5 个服务 STATE 均为 Up（db healthy / backend healthy / frontend healthy / worker Up / redis Up）；
- 浏览器开 `https://your-domain.com` → 注册/登录 流程走通（验证码走真实邮件服务，需要后端 `.env` 的 SMTP_* 已填；未填时 SMTP 失败会在后端日志打 warn，不影响其他功能）；
- Secure Cookie 生效：F12 Application → Cookies → 你的域名 → `auth_session` 列 `Secure/HttpOnly/SameSite=Lax` 三个勾 ✓。

### B.4 失败回退路径

| 症状 | 根因与处理 |
|---|---|
| B.2-4a 报 502 Bad Gateway | 前端容器 `cs-website` 未就绪；`make logs frontend --tail 50` 看 next build 是否完成；首次构建久等即可 |
| HTTPS 访问 400 / 无限重定向登录页 | `TRUST_PROXY` 仍为 false；改 `.env` 后 `make rebuild frontend` 重启；或反代未传 `X-Forwarded-Proto: https` |
| 反代 502 端口 2333 不通 | 宿主机防火墙（ufw/firewalld）禁止反代连 2333；或 compose 端口映射漏了 `127.0.0.1:2333:3000`（双端口别写反） |
| 上传文件 413 Request Entity Too Large | nginx `client_max_body_size` 未加；或前端 `next.config.ts` 未开 body size；或后端 nginx/反代两者都要加最小值中最大那方 |

---

## 场景 C：健康检查 + 运维端点验收（目标：6 条端点 + 探针 + 告警最小集配置完成）

**适用**：部署 B 场景完成后，第一时间验收运维面，确保 SLO/G 场景可运行。

### C.1 6 条运维端点（逐个 curl 验收）

```bash
# 在生产服务器本机执行（跳反代，直接探容器内网 BFF 转发或后端直连）
TARGET=http://127.0.0.1:2333

curl -s -w "\nHTTP %{http_code}\n" $TARGET/api/health           # C-1 → {"status":"ok"} / 200（liveness 浅）
curl -s -w "\nHTTP %{http_code}\n" $TARGET/api/health/events    # C-2 → JSON 含监听器数量 / 200（事件总线链路）
curl -s -w "\nHTTP %{http_code}\n" $TARGET/api/health/security  # C-3 → 限流/黑名单/迁移状态 / 200
curl -s -w "\nHTTP %{http_code}\n" $TARGET/api/readyz           # C-4 → 200 或 503（readiness；不通 MUST 503）
# 以下两条需要 system:monitor 权限（用超级用户 Bearer 或调后端容器内 curl 走 localhost）：
docker compose exec -T backend curl -s -H "Authorization: Bearer <superuser-token>" http://localhost:8000/metrics/json   # C-5 → 200 JSON 指标
docker compose exec -T backend curl -s -H "Authorization: Bearer <superuser-token>" http://localhost:8000/status         # C-6 → 200 组件明细
```

> 端点挂在后端 `root_router`，路径是 `/health`、`/readyz`（**不**带 `/api/v1`）。前端 BFF 的 `/api/health` 就是转发到后端 `/health`，所以 C-1 同时验了 BFF 转发链。

### C.2 探针配置（给 docker compose / Kubernetes 用；以下为 compose 已推荐写法）

在 `docker-compose.yml` 中，以下两项 **SHOULD** 已有（缺失时补上并 `make up` 重启）：

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8000/readyz"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
  frontend:
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/api/health"]
      interval: 20s
      timeout: 5s
      retries: 3
```

### C.3 成功标准

- C-1~C-4 全部 HTTP 200（C-4 在 DB 正常时 200；你手动停 db 验证它会切 503 更好，但不强制）。
- C-5/C-6 带上管理员 Bearer 后 HTTP 200。
- `make ps` 显示 backend/frontend 有 `(healthy)` 后缀（健康检查生效）。

### C.4 失败回退路径

| 症状 | 处理 |
|---|---|
| C-4 长期 503 | `make logs backend --tail 50` 查 DB 连接错误；根 `.env` 的 `DATABASE_HOST=db` 是否正确 |
| C-5/C-6 401 | 少了 Bearer；或用户没 `system:monitor` 权限；后端直调临时用 `docker compose exec -T backend curl http://localhost:8000/metrics/json` 跳过鉴权也行 |
| healthcheck 一直 starting → unhealthy | 容器里没装 `wget`；换 `["CMD-SHELL", "curl -fs http://localhost:8000/readyz || exit 1"]` |

---

## 场景 D：数据备份 + 异地传输（目标：每日 03:00 自动备份 + 手工导出随时可跑）

**适用**：所有有持久化数据的部署（本地开发可选；生产 MUST 启用 cron）。

### D.1 手动备份（迁移/升级前 MUST 跑一次）

```bash
cd <project-root>

# D.1-1 推荐：根级 export 脚本（直接拷到 ~/Desktop 或任意目录；已处理 DATABASE_HOST=db 的容器内网→localhost 回退）
./scripts/ops/export_db_to_desktop.sh                      # 默认输出到 ~/Desktop
./scripts/ops/export_db_to_desktop.sh /opt/cs-backup/manual # 或指定输出目录

# D.1-2 可选：后端专用备份脚本（pg_dump --format=custom + gzip + 完整性校验）
./CS-Web-Backend/tools/scripts/db/backup_db.sh /opt/cs-backup/manual

# D.1-3 异地传输（任选其一；禁止邮件/IM 传输，禁止未加密上传）
# 方式 A：scp 到异地备份机
scp /opt/cs-backup/manual/domefff_*.sql.gz backup-user@backup-host:/opt/cs-backup/$(hostname)/
# 方式 B：对象存储（S3/OSS 兼容）
aws s3 cp /opt/cs-backup/manual/domefff_*.sql.gz s3://your-bucket/fztbucs-db-backups/$(hostname)/ --sse AES256

# D.1-4 同时备份上传的静态文件（data/ 卷：头像 avatars/、社区图 community-images/ 等）
tar -czf /opt/cs-backup/manual/data-static-$(date +%Y%m%d-%H%M).tar.gz data/
rsync -av /opt/cs-backup/manual/data-static-*.tar.gz backup-user@backup-host:/opt/cs-backup/$(hostname)/
```

### D.2 每日自动 cron（生产 MUST 配；03:00 低峰）

```bash
# crontab -e 写入以下两行（路径改成你服务器绝对路径）
0 3 * * * cd /opt/FztbuCS-Project && ./CS-Web-Backend/tools/scripts/db/backup_db.sh /opt/cs-backup/daily >> /var/log/fztbucs-backup.log 2>&1
15 3 * * * /usr/bin/rsync -av --delete /opt/cs-backup/daily/ backup-user@backup-host:/opt/cs-backup/$(hostname)/daily/ >> /var/log/fztbucs-backup-rsync.log 2>&1
```

> `backup_db.sh` 已内置「保留 14 天自动清理」；与 SLO 目标 G-3 一致（备份保留 14 天）。

### D.3 成功标准

- D.1 脚本结束 `echo $?` 返回 0；输出文件大小 > 100KB（空库也有 schema，小于 100KB 说明导出失败）。
- `gunzip -t <backup>.sql.gz` 完整性校验通过。
- 手动 `cat /var/log/fztbucs-backup.log` 没有 ERROR。

### D.4 失败回退路径

| 症状 | 处理 |
|---|---|
| `connection to database "domefff" failed` | `DATABASE_HOST=db` 是容器内网名；在宿主机跑需要 `DATABASE_HOST_OVERRIDE=localhost ./scripts/ops/export_db_to_desktop.sh`（脚本内置自动回退，未生效时显式传） |
| `pg_dump: error: permission denied` | 用的不是超级用户；DB 备份 MUST 用 `postgres` 或 `--no-owner` 模式，脚本已默认加 `--no-owner --no-privileges` |
| scp/rsync 传输失败 | ssh key 不在 backup-host authorized_keys；或备份目录没写权限；先手动 `ssh backup-user@backup-host ls /opt/cs-backup` 打通 |

---

## 场景 E：从备份恢复 + 开发库→生产库迁移（目标：恢复后 5 张关键表行数对账通过）

**适用**：故障恢复 / 首次从开发库向空的生产库迁移。**两种模式分开选路径**，不要混走。

### E.1 模式 A：恢复到空生产库（推荐；首次上线或清空重建后）

```bash
cd /path/to/prod/FztbuCS-Project

# E.1-1 只起 db 服务（先别起 backend；避免迁移中写请求）
docker compose down
docker compose up -d db
sleep 10 && docker compose ps   # db Up (healthy)

# E.1-2 用 backend 备份脚本的 --restore 模式（读生产 .env 连接参数）
./CS-Web-Backend/tools/scripts/db/backup_db.sh --restore /opt/cs-backup/domefff_2026-08-20_0300.sql.gz

# E.1-3 脚本内部已自动重建序列；手动确认所有自增序列对齐最大值（可选，脚本已做但二次验更稳）
docker compose exec -T db psql -U postgres -d domefff -c "
  SELECT tbl.relname AS table_name,
         setval(pg_get_serial_sequence(tbl.relname,'id'),
                COALESCE((SELECT MAX(id) FROM \"\"\"||tbl.relname||\"\"\"),1)) AS setval_done
  FROM pg_class tbl JOIN pg_namespace ns ON ns.oid = tbl.relnamespace
  WHERE tbl.relkind='r'
    AND EXISTS (SELECT 1 FROM information_schema.columns c
                WHERE c.table_schema='public' AND c.table_name=tbl.relname
                  AND c.column_name='id' AND c.data_type='integer');"

# E.1-4 全栈起来验证
make up        # backend/frontend/worker 全起
```

### E.2 模式 B：生产已有 seed 数据（admin + 预置角色，不能丢）

直接灌会撞 `users.email` 唯一约束或主键/序列冲突。**SHOULD 用清空 pgdata 卷后走 A 模式**（seed 数据本就是一次性的，恢复后从备份里已经有完整的 admin 角色权限）：

```bash
# 停全栈 + 删卷 + 重建 db 空容器
docker compose down
docker volume ls | grep fztbucs.*_pgdata   # 确认卷名
docker volume rm fztbucs-project_pgdata    # 卷名按上条输出替换
docker compose up -d db
# → 然后切回 E.1-2 ~ E.1-4
```

> 如果必须保留 seed 数据（极端场景）：走 `RootDoc-MigEval.md` §4 的「按 email/username 去重 + INSERT ... ON CONFLICT DO NOTHING」策略（步骤多，这里不展开；恢复 MUST 优先 A 模式最小化人为错误）。

### E.3 5 张关键表行数对账（恢复成功 MUST 全通过）

```bash
docker compose exec -T db psql -U postgres -d domefff -c "
  SELECT 'users'            AS t, COUNT(*) FROM users
  UNION ALL SELECT 'roles',         COUNT(*) FROM roles
  UNION ALL SELECT 'exams',         COUNT(*) FROM exams
  UNION ALL SELECT 'events',        COUNT(*) FROM events
  UNION ALL SELECT 'community_posts', COUNT(*) FROM community_posts;"
```

**成功判定**：5 张表行数与源库（备份导出前）偏差 ≤ 0.1%；`roles` 表 MUST 完全一致（角色枚举不能少）。

再附加 3 条登录/权限验证：
```bash
# 验证 1：后端直连 /auth/login 用旧备份的 admin 账号仍可拿 token
# 验证 2：前端 HTTPS 登录页正常登录（密码哈希懒升级 scrypt→bcrypt 由后端自动处理，首次登录成功后升级完成）
# 验证 3：管理员仍有所有预置权限（RBAC seed 未被覆盖）
```

### E.4 开发库→生产库迁移补充（非备份恢复纯迁移）

1. **MUST 先导出前停开发环境写入**（`make down` 或 at least 把应用切只读），避免导出后增量漏迁。
2. **MUST 生产密钥与开发不同**（4 条密钥全部重生成）：用户密码哈希存储格式与密钥无关（scrypt/bcrypt 自带 salt），可正常登录后懒升级。
3. **SHOULD 迁移后 72 小时双写比对**（仅关键业务表 users/exams/events），确认生产与开发最终一致后再下线开发。
4. **MUST 走 D 场景做备份**：迁移完成后当天做一次全量备份，并验证恢复（季度演练的要求见场景 G §G.5）。

### E.5 失败回退路径（恢复失败 MUST 不丢备份）

> 铁律：**恢复脚本/命令永远不会主动删备份文件；失败时先换个库名试恢复，确认备份本身没坏再做破坏性操作**。

| 症状 | 处理 |
|---|---|
| pg_restore 报 `input file does not appear to be a valid archive` | 备份不是 custom 格式；你传的是 `.sql`（纯文本）应改用 `psql -f`；或 gzip 没解压先 `gunzip -k` |
| 撞 `users_pkey` 唯一约束（模式 B 未清卷） | 按 E.2 清 pgdata 走模式 A；或手工 `TRUNCATE users CASCADE` 后重灌（清 admin 风险大，优先 A） |
| 登录后所有用户查不到角色/权限（RBAC 表为空） | 备份导出时漏了 `roles/permissions/role_permissions/user_roles` 表；从 D 场景取另一份备份重恢复；必要时 `services/rbac/rbac_seed_data.py` 再 init 一遍（会重建 admin 默认密码，改完后 MUST 立即改密） |

---

## 场景 F：版本升级回滚（目标：发版失败 10 分钟内恢复到上个稳定版本）

**适用**：合入 release 分支后全栈升级，但某端冒烟失败（登录白屏 / 关键路径 5xx / 迁移 break）。回滚要分层：前端无状态快回；后端+迁移需要先确认迁移可逆。

### F.1 发版前 MUST 做的 3 件事（不做就别发版）

1. `make tag <new-version>` 打 git tag 并 push（三仓都要打；具体命令见 Makefile）；没 tag 就无法切回已知稳定 SHA。
2. **先跑场景 D**：备份数据库 + 异地传输；并 **额外** 把当前生产镜像打 tag：
   ```bash
   docker tag fztbucs-project-backend:latest fztbucs-project-backend:$(cat version.txt)-pre
   ```
3. 确认 Alembic 迁移链**可逆**：
   ```bash
   cd CS-Web-Backend && source .venv/bin/activate
   alembic current        # 记录当前 revision，例：abc123
   alembic upgrade head   # 新迁移跑通；若 upgrade 失败，F.3 回滚
   ```

### F.2 发版流程（标准升级）

```bash
# F.2-1 拉最新代码 + 同步子模块指针（根仓 Makefile 已封装）
make pull

# F.2-2 备份，见场景 D（发版前 MUST 最后做一次）
./scripts/ops/export_db_to_desktop.sh /opt/cs-backup/pre-release

# F.2-3 重建 + 重启
make rebuild        # = docker compose up -d --build --force-recreate
```

**F.2 成功验收**：场景 C 的 6 条端点全 200 + 场景 B 的 HTTPS 登录/注册通。任何关键冒烟失败 → 立即走 F.3。

### F.3 回滚步骤（≤ 10 分钟止损）

```bash
# F.3-1 前端最快回滚（纯无状态，1 分钟内）：
#  回到上次发布的镜像 tag（F.1 第 2 条打的 pre 镜像或旧 git tag 对应镜像）
docker compose up -d --force-recreate \
  --scale frontend=0 \
  && docker tag fztbucs-project-frontend:$(cat version.txt)-pre fztbucs-project-frontend:latest \
  && docker compose up -d --no-build frontend

# F.3-2 若问题出在后端（比如迁移 break），先停 backend + worker，回迁移：
docker compose stop backend worker
cd CS-Web-Backend && source .venv/bin/activate
alembic downgrade -1          # 或 alembic downgrade <F.1 记录的旧 revision>
# 然后用旧镜像起 backend/worker：
docker tag fztbucs-project-backend:$(cat version.txt)-pre fztbucs-project-backend:latest
docker compose up -d --no-build backend worker

# F.3-3 代码级回滚（前两条都救不了，用 git 整仓回到上次 tag）：
git checkout <last-stable-tag>
git submodule update --init --recursive
make rebuild   # 从头 build 对应版本镜像；耗时 ≈ 首次构建
```

### F.4 成功标准（回滚达成）

- 场景 C 6 条端点全 200。
- 登录/登出/发帖/报名 4 条核心路径（Onboarding §5）全部走通。
- F.3-2 回迁移后 `alembic current` 输出 revision 与发版前一致；`ERRNO` 表里没遗留新版本字段（后端 `/status` 接口明细核对）。

### F.5 失败回退路径（回滚本身也失败）

- **最后救命稻草 = D 场景的备份**：清空 pgdata 卷（E.2 模式 B）→ E.1 模式 A 恢复旧备份 → 用旧镜像启动全栈。
- **备份也救不了**：立即在反代层返回维护页（nginx 503 return + retry_after），避免用户继续写脏数据；同步 P0 告警。

---

## 场景 G：SLO 对齐 + 可观测性最小集 + 巡检日历（目标：月度 SLO 报告自动跑）

**适用**：SRE/运维接岗后，给根级编排层建立统一的稳定性基线。端侧专项指标（前端 BFF 端点错误预算 / 后端 OTel 详情）分别去 FrontDoc-Ops.md Part B / BackDoc-Infra.md，本文不重述。

### G.1 SLO 目标表（根级编排层单一事实源）

| 维度 | 指标 | 目标 | 测量方式 | 权威实现位置 |
|---|---|---|---|---|
| 可用性 | API 可用性 | **99% / 月**（月停机 ≤ 432 分钟） | `/health` + `/readyz` 探针成功率，按月聚合 | 根 ci.yml Uptime 工作流 |
| 可用性 | 前端页面可用性 | **99% / 月** | 首页 `GET /` HTTP 200 成功率（外部探针） | 外部 uptime 监控服务或自建 |
| 延迟 | API p95 | **< 500ms** | FastAPI 访问日志 `duration_ms` | 后端 loguru JSON 字段 |
| 延迟 | API p99 | **< 2000ms** | 同上 | 同上 |
| 延迟 | 前端 LCP | **< 2.5s**（1.1 接入 RUM 后正式考核） | Performance API / Web Vitals | 前端 RUM（预留）|
| 持久化 | 备份 RPO | **≤ 24h** | 场景 D 每日 03:00 cron 全量 | `backup_db.sh` 时间戳核对 |
| 持久化 | 备份 RTO | **≤ 4h** | 从备份恢复到服务全 200 | 季度演练实际计时 |
| 持久化 | 备份保留 | **14 天** | 14 天前自动清理（脚本内置） | `backup_db.sh` rm 逻辑 |

月度错误预算 = `43200 分钟 × 1% = 432 分钟/月`。**预算耗尽 MUST**：冻结非紧急变更，集中稳定性修复；评审是否调 SLO 目标（而非放松）。

### G.2 可观测性最小集（1.0.x，不依赖 Prometheus）

以下最小集通过日志+脚本即可跑，无需引入新的监控基础设施（完整版见 BackDoc-Infra.md OTel）。

**G.2-1 关键字段对齐**

| 组件 | 日志格式 | 必须字段 |
|---|---|---|
| 后端 | loguru JSON（prod profile） | `timestamp, level, request_id, user_id, method, path, status, duration_ms` |
| 前端 BFF | pino NDJSON | `timestamp, level, request_id, msg` |

轮转：后端 10MB × 30 天文件轮转；前端按部署日志方案。

**G.2-2 告警最小集 5 条（SCRIPT / 日志监控实现）**

| 告警 | 触发条件 | 级别 | 通知 |
|---|---|---|---|
| 服务不可用 | `/health` 连续 3 次失败（间隔 10s） | P0 | 邮件 + IM 群机器人 |
| 数据库不可达 | `/readyz` 连续 2 次 503 | P0 | 邮件 + IM |
| 错误率飙升 | 5 分钟窗口 5xx > 5% | P1 | 日志告警面板 |
| 备份失败 | `backup_db.sh` exit ≠ 0 | P1 | cron 日志每日巡检 |
| 磁盘预警 | 数据卷 > 85% | P1 | 系统 df |

**G.2-3 OTel（可选增强；默认关闭 `OTEL_ENABLED=False`）**

启用只需在根 `.env` 加：
```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
OTEL_SERVICE_NAME=cs-web-backend
```
启用后 FastAPI / SQLAlchemy / Redis 自动埋点；traces + metrics OTLP 推到 collector → Grafana。

### G.3 巡检日历（根级运维）

| 频率 | 必做项 |
|---|---|
| **每日** | ① 备份脚本成功（`ls -lt /opt/cs-backup/daily/` 最新文件 < 27h）；② ERROR 日志条目逐条过 |
| **每周** | ① 磁盘 < 85%；② `/readyz` 200；③ 告警最小集 5 条无红灯 |
| **每月** | ① 生成月度 SLO 报告（可用性、p95/p99、RPO、错误预算消耗）；② 评估是否调 SLO 目标；③ 评审告警有效性（误报/漏报） |
| **每季度** | ① 执行一次恢复演练（E 场景，备份→恢复→行数对账，实际计时验证 RTO ≤ 4h）；② 巡检 SSL 证书有效期（≤ 30 天 MUST 续期） |

### G.4 成功标准

- 月度 SLO 报告可一键生成（`scripts/ops/gen_slo_report.py`，如无脚本可按 §G.1 手动摘），4 项 100% 达标或在预算内。
- 告警最小集 5 条至少在最近一周有真实触发（或手工注入演练），通知链路可达接收人。
- 最近一次季度恢复演练结果 ≤ RTO 目标 4h，关键表行数对账 ≤ 0.1% 偏差；记录在 CHANGELOG 的 R 表。

### G.5 失败回退路径

| 症状 | 处理 |
|---|---|
| 月度 SLO 连续 2 月不达标 | 进入「错误预算耗尽」模式：冻结功能发版，集中做稳定性；评审 §G.1 指标目标是否合理（如 p95 500ms 对 3MB 首站不合理则调目标，但必须写 ADR 说明调整动机） |
| 告警长期不报（P0/P1 全绿但实际出故障没人管） | 立即做一次「手工注入」验证告警链路：停 db 10 秒看 P0 是否通知到人；通知不到 MUST 修机器人 webhook / 邮件列表再恢复 |
| 季度恢复演练 RTO > 4h | 复盘哪一步慢：备份下载 / pg_restore / 序列重建 / 冷启动；对应优化（加 1Gbps 备份专线 / 预预热 PG shared_buffers / 序列脚本改逐表并行） |

---

## 场景 H（附加）：CI 双轨分工（GitHub Actions vs Jenkins）

> 与 Backend/Frontend 子仓内部署不同，根仓关注「**合入门禁的权威在哪**」。两套 CI 并存，分工明确如下（避免双轨维护漂移）：

| 系统 | 角色 | 触发 | 独有能力 | 备注 |
|---|---|---|---|---|
| GitHub Actions `.github/workflows/ci.yml` | **主验证门禁（活化）** | `push` / `pull_request` → `main` / `master` + `workflow_dispatch` | G1 安全扫描 `scan_security.py`；ER-45 PR diff 覆盖率 `diff_coverage.py`；ER-09 文档死链 `check_dead_links.py --base . --docs docs` | 功能最全；合入门禁单一权威 |
| 后端 `Jenkinsfile` | **等价备用验证（自托管 runner）** | Jenkins 控制器按需触发 | 自托管 runner 可连内网制品库；与 docker-compose.ci.yml 同固定端口 54329/63799 | 当前**不做部署**，仅做与 Actions 对等的「验证体」，防止 GitHub 宕机时门禁真空；契约冻结步（openapi.baseline.json）在此执行（Actions 因 submodule 拿不到根仓基线，已于 2026-08-17 移除该步） |

> 两者都只做「验证」，**不包含部署/发布阶段**（部署 = 场景 B / F，手动或 GitOps 另做）。

---

## §S：成功标准总表（7 场景结果一览，上线前最后过一遍）

| 场景 | 验收命令 / 动作 | 期望结果 | 本节对应 |
|---|---|---|---|
| A 本地开发起 | 3 条 curl（§A.2） | 全 200 | A.2 |
| B 容器全栈 HTTPS | HTTPS `curl -sI`（§B.2-6a/b） | 200 + HSTS 头 | B.3 |
| C 运维端点 | 6 条端点 curl（§C.1） | 全 200 | C.3 |
| D 备份异地 | `gunzip -t <backup>.sql.gz` + 异地 `ls` | 完整性 OK + 文件存在 | D.3 |
| E 恢复迁移 | 5 关键表行数对账（§E.3） | 偏差 ≤ 0.1% | E.3 |
| F 发版回滚 | `alembic current` == 旧 rev + C 场景全通 | 全满足 | F.4 |
| G SLO + 巡检 | 月度报告 4 项达标 + 恢复演练 ≤ 4h | 全达标 | G.4 |

---

> ↩ **返回根级文档地图**：[README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/README.md) · **配套 Tutorial（新人先学）**：[Onboarding.md](Onboarding.md) · **端侧专项运维 Runbook**：[BackDoc-Infra.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-Infra.md) / FrontDoc-Ops.md · **跨仓工程红线**：[RootDoc-EngConv.md](RootDoc-EngConv.md)
