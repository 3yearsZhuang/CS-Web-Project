# API 参考（FztbuCS-Project）

> 本文件由 `openapi.baseline.json`（0.9.8 冻结契约）自动生成，**请勿手改**；契约变更时重新生成或同步更新 baseline。
> 基础路径：`/api/v1`；认证：`OAuth2PasswordBearer`（`Authorization: Bearer <token>`）；传输格式：camelCase。


## RBAC权限管理

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/rbac/me/permissions` | Get My Permissions | 是 | - | UserPermissionsResponse |
| GET | `/api/v1/rbac/me/roles` | Get My Roles | 是 | - | - |
| GET | `/api/v1/rbac/permissions` | Get Permissions | 是 | - | PaginatedResponse_Permission_ |
| POST | `/api/v1/rbac/permissions` | Create Permission | 是 | PermissionCreate | Permission |
| DELETE | `/api/v1/rbac/permissions/{permission_id}` | Delete Permission | 是 | - | - |
| GET | `/api/v1/rbac/permissions/{permission_id}` | Get Permission | 是 | - | Permission |
| PUT | `/api/v1/rbac/permissions/{permission_id}` | Update Permission | 是 | PermissionUpdate | Permission |
| GET | `/api/v1/rbac/roles` | Get Roles | 是 | - | PaginatedResponse_Role_ |
| POST | `/api/v1/rbac/roles` | Create Role | 是 | RoleCreate | Role |
| DELETE | `/api/v1/rbac/roles/{role_id}` | Delete Role | 是 | - | - |
| GET | `/api/v1/rbac/roles/{role_id}` | Get Role | 是 | - | Role |
| PUT | `/api/v1/rbac/roles/{role_id}` | Update Role | 是 | RoleUpdate | Role |
| DELETE | `/api/v1/rbac/roles/{role_id}/permissions/{permission_id}` | Revoke Permission From Role | 是 | - | - |
| POST | `/api/v1/rbac/roles/{role_id}/permissions/{permission_id}` | Assign Permission To Role | 是 | - | - |
| POST | `/api/v1/rbac/users/{user_id}/check-permission` | Check User Permission | 是 | UserPermissionCheck | UserPermissionResult |
| GET | `/api/v1/rbac/users/{user_id}/permissions` | Get User Permissions | 是 | - | UserPermissionsResponse |
| GET | `/api/v1/rbac/users/{user_id}/roles` | Get User Roles | 是 | - | - |
| DELETE | `/api/v1/rbac/users/{user_id}/roles/{role_id}` | Revoke Role From User | 是 | - | - |
| POST | `/api/v1/rbac/users/{user_id}/roles/{role_id}` | Assign Role To User | 是 | - | - |

## workbench

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/workbench/contributions/github` | GitHub 贡献热力图（近一年数据，6h 缓存）。 | 是 | - | GithubContributionsOut |
| POST | `/api/v1/workbench/focus-sessions` | 番茄钟完成一轮专注后上报记录（幂等不校验重复，前端只报完成轮）。 | 是 | FocusSessionIn | FocusSessionOut |
| GET | `/api/v1/workbench/llm-config` | 读取用户 LLM 配置（脱敏：apiKey 只回显掩码，不回传明文）。 | 是 | - | LlmConfigOut |
| PUT | `/api/v1/workbench/llm-config` | 保存用户 LLM 配置（API Key AES-256-GCM 加密存储，绝不落明文/日志）。 | 是 | LlmConfigIn | LlmConfigUpdateOut |
| GET | `/api/v1/workbench/stats/api-usage` | API 调用统计：今日计数 + 近 N 天趋势 + endpoint 分布。 | 是 | - | ApiUsageStats |
| GET | `/api/v1/workbench/stats/llm-usage` | 学习助手 LLM 用量：调用次数 / token 消耗 / 近 N 天趋势 / 模型分布。 | 是 | - | LlmUsageStats |
| GET | `/api/v1/workbench/stats/pomodoro` | 番茄钟专注统计：总轮数 / 总时长 / 今日 / 近 N 天分布（喂给学习助手 Skill）。 | 是 | - | PomodoroStats |

## 个人资料

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/avatars/{filename}` | Serve Avatar | - | - | - |
| GET | `/api/v1/profile` | Get Profile | 是 | - | ProfileResponse |
| PUT | `/api/v1/profile` | Update Profile | 是 | ProfileUpdate | UserOut |
| POST | `/api/v1/profile/avatar/preset` | Set Preset Avatar | 是 | AvatarPresetRequest | UserOut |
| POST | `/api/v1/profile/avatar/upload` | Upload Avatar | 是 | - | UserOut |
| POST | `/api/v1/profile/password` | Change Password | 是 | ChangePasswordRequest | - |

## 入社申请

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| POST | `/api/v1/join` | Submit Application | - | JoinApplicationInput | - |
| GET | `/api/v1/join/admin` | List Applications | 是 | - | - |
| PATCH | `/api/v1/join/admin/{application_id}` | Review Application | 是 | JoinReviewRequest | JoinApplicationOut |
| GET | `/api/v1/join/mine` | List Mine | 是 | - | - |

## 公告

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/announcements` | List Active Announcements | - | - | - |
| GET | `/api/v1/announcements/admin` | List All Announcements | 是 | - | - |
| POST | `/api/v1/announcements/admin` | Create Announcement | 是 | AnnouncementInput | AnnouncementOut |
| DELETE | `/api/v1/announcements/admin/{announcement_id}` | Delete Announcement | 是 | - | - |
| GET | `/api/v1/announcements/admin/{announcement_id}` | Get Announcement | 是 | - | AnnouncementOut |
| PATCH | `/api/v1/announcements/admin/{announcement_id}` | Update Announcement | 是 | AnnouncementInput | AnnouncementOut |
| POST | `/api/v1/announcements/admin/{announcement_id}/toggle` | Toggle Announcement | 是 | - | AnnouncementOut |

## 学习助手

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| POST | `/api/v1/auxilio/chat` | SSE 流式对话：支持 OpenAI / Anthropic 双协议与 Skills 工具调用。 | 是 | ChatRequest | SSE (text/event-stream) |
| GET | `/api/v1/auxilio/conversations` | 列出当前用户的学习助手会话（按更新时间倒序）。 | 是 | - | ConversationListOut |
| GET | `/api/v1/auxilio/conversations/{conversation_id}/messages` | 获取会话内的消息列表（按时间正序）。 | 是 | - | ChatMessageListOut |

## 审计日志

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| DELETE | `/api/v1/audit/logs` | Delete Audit Logs Before | 是 | - | - |
| GET | `/api/v1/audit/logs` | List Audit Logs | 是 | - | PaginatedResponse_AuditLogItem_ |
| POST | `/api/v1/audit/logs` | Create Audit Log | 是 | CreateAuditLogRequest | - |
| DELETE | `/api/v1/audit/logs/{log_id}` | Delete Audit Log | 是 | - | - |
| GET | `/api/v1/audit/logs/{log_id}` | Get Audit Log | 是 | - | AuditLogItem |

## 密码重置审批

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/admin/password-resets` | List Reset Requests | 是 | - | - |
| POST | `/api/v1/admin/password-resets/{request_id}/approve` | Approve Reset Request | 是 | ResetRequestResolve | ResetRequestOut |
| POST | `/api/v1/admin/password-resets/{request_id}/reject` | Reject Reset Request | 是 | ResetRequestResolve | ResetRequestOut |

## 工具集

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/tools/admin/exam` | Admin List Exams | 是 | - | - |
| POST | `/api/v1/tools/admin/exam` | Create Exam | 是 | ExamInput | - |
| DELETE | `/api/v1/tools/admin/exam/{exam_id}` | Delete Exam | 是 | - | - |
| PUT | `/api/v1/tools/admin/exam/{exam_id}` | Update Exam | 是 | ExamInput | - |
| POST | `/api/v1/tools/admin/exam/{exam_id}/end` | End Exam | 是 | - | - |
| POST | `/api/v1/tools/admin/exam/{exam_id}/publish` | Publish Exam | 是 | - | - |
| GET | `/api/v1/tools/admin/exam/{exam_id}/questions` | Admin List Questions | 是 | - | - |
| POST | `/api/v1/tools/admin/exam/{exam_id}/questions` | Create Question | 是 | QuestionInput | - |
| DELETE | `/api/v1/tools/admin/exam/{exam_id}/questions/{question_id}` | Delete Question | 是 | - | - |
| PUT | `/api/v1/tools/admin/exam/{exam_id}/questions/{question_id}` | Update Question | 是 | QuestionInput | - |
| GET | `/api/v1/tools/admin/exam/{exam_id}/ranking` | Exam Ranking | 是 | - | - |
| POST | `/api/v1/tools/admin/resource` | Review Resource | 是 | - | - |
| POST | `/api/v1/tools/admin/task` | Create Task | 是 | TaskInput | - |
| GET | `/api/v1/tools/admin/task/claims/pending` | Pending Claims | 是 | - | - |
| POST | `/api/v1/tools/admin/task/claims/{claim_id}/review` | Review Claim | 是 | - | - |
| DELETE | `/api/v1/tools/admin/task/{task_id}` | Delete Task | 是 | - | - |
| PUT | `/api/v1/tools/admin/task/{task_id}` | Update Task | 是 | TaskInput | - |
| POST | `/api/v1/tools/admin/task/{task_id}/close` | Close Task | 是 | - | - |
| POST | `/api/v1/tools/admin/task/{task_id}/publish` | Publish Task | 是 | - | - |
| GET | `/api/v1/tools/auxilio` | Auxilio Analysis | 是 | - | - |
| GET | `/api/v1/tools/component-registry` | List Components | - | - | - |
| POST | `/api/v1/tools/component-registry` | Create Component | 是 | ComponentItemInput | - |
| DELETE | `/api/v1/tools/component-registry/{item_id}` | Delete Component | 是 | - | - |
| GET | `/api/v1/tools/component-registry/{item_id}` | Get Component | - | - | - |
| PUT | `/api/v1/tools/component-registry/{item_id}` | Update Component | 是 | ComponentItemInput | - |
| PUT | `/api/v1/tools/component-registry/{item_id}/guide` | Update Guide | 是 | ComponentGuideInput | - |
| PUT | `/api/v1/tools/component-registry/{item_id}/variants` | Replace Variants | 是 | - | - |
| POST | `/api/v1/tools/component-registry/{item_id}/variants/{variant_id}/toggle` | Toggle Variant | 是 | - | - |
| GET | `/api/v1/tools/exam` | List Exams | - | - | PaginatedResponse_dict_ |
| GET | `/api/v1/tools/exam/{exam_id}` | Get Exam | - | - | - |
| GET | `/api/v1/tools/exam/{exam_id}/my-results` | My Results | 是 | - | - |
| GET | `/api/v1/tools/exam/{exam_id}/questions` | List Exam Questions | - | - | - |
| POST | `/api/v1/tools/exam/{exam_id}/submit` | Submit Answers | 是 | ExamSubmitIn | - |
| GET | `/api/v1/tools/points` | My Points | 是 | - | - |
| GET | `/api/v1/tools/points/leaderboard` | Leaderboard | - | - | - |
| GET | `/api/v1/tools/resource` | List Resources | - | - | - |
| POST | `/api/v1/tools/resource` | Create Resource | 是 | ResourceInput | - |
| GET | `/api/v1/tools/resource/files/{filename}` | Serve Resource File | - | - | - |
| POST | `/api/v1/tools/resource/upload` | Upload Resource File | 是 | - | - |
| GET | `/api/v1/tools/resource/{resource_id}` | Get Resource | - | - | - |
| GET | `/api/v1/tools/task` | List Tasks | - | - | - |
| GET | `/api/v1/tools/task/claims/mine` | My Claims | 是 | - | - |
| DELETE | `/api/v1/tools/task/claims/{claim_id}` | Cancel Claim | 是 | - | - |
| POST | `/api/v1/tools/task/claims/{claim_id}/submit` | Submit Claim | 是 | - | - |
| GET | `/api/v1/tools/task/{task_id}` | Get Task | - | - | - |
| POST | `/api/v1/tools/task/{task_id}/claim` | Claim Task | 是 | - | - |
| GET | `/api/v1/tools/task/{task_id}/claims` | Task Claims | - | - | - |

## 异常管理

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/exceptions/logs` | Get Exception Logs | 是 | - | PaginatedResponse_ExceptionLogItem_ |
| GET | `/api/v1/exceptions/logs/{log_id}` | Get Exception Log | 是 | - | ExceptionLogItem |
| PUT | `/api/v1/exceptions/logs/{log_id}/resolve` | Resolve Exception Log | 是 | - | ExceptionLogResolveResponse |

## 活动

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/events` | List Events | - | - | PaginatedResponse_EventOut_ |
| GET | `/api/v1/events/me/registered` | List Registered | 是 | - | - |
| GET | `/api/v1/events/{event_id}` | Get Event | - | - | EventOut |
| DELETE | `/api/v1/events/{event_id}/register` | Cancel Registration | 是 | - | - |
| POST | `/api/v1/events/{event_id}/register` | Register Event | 是 | EventRegistrationInput | EventRegistrationOut |
| GET | `/api/v1/events/{event_id}/registration` | Get Registration | 是 | - | EventRegistrationOut |

## 用户管理

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/users/` | Read Users | 是 | - | PaginatedResponse_User_ |
| POST | `/api/v1/users/` | Create User | 是 | UserCreate | User |
| GET | `/api/v1/users/me` | Read User Me | 是 | - | User |
| PUT | `/api/v1/users/me` | Update User Me | 是 | UserUpdate | User |
| DELETE | `/api/v1/users/{user_id}` | Delete User | 是 | - | - |
| GET | `/api/v1/users/{user_id}` | Read User | 是 | - | User |
| PUT | `/api/v1/users/{user_id}` | Update User | 是 | UserUpdate | User |

## 社区

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/community/categories` | List Categories | - | - | - |
| DELETE | `/api/v1/community/comments/{comment_id}` | Delete Comment | 是 | - | - |
| PUT | `/api/v1/community/comments/{comment_id}` | Update Comment | 是 | - | - |
| GET | `/api/v1/community/comments/{comment_id}/nested` | List Nested Comments | - | - | - |
| GET | `/api/v1/community/drafts` | List Drafts | 是 | - | - |
| GET | `/api/v1/community/favorites` | List Favorites | 是 | - | - |
| POST | `/api/v1/community/favorites` | Toggle Favorite | 是 | - | - |
| GET | `/api/v1/community/follows` | List Follows | 是 | - | - |
| POST | `/api/v1/community/follows` | Toggle Follow | 是 | - | - |
| GET | `/api/v1/community/images/{filename}` | Serve Community Image | - | - | - |
| GET | `/api/v1/community/members` | List Members | - | - | - |
| GET | `/api/v1/community/posts` | List Posts | 是 | - | PaginatedResponse_dict_ |
| POST | `/api/v1/community/posts` | Create Post | 是 | - | - |
| GET | `/api/v1/community/posts/slug/{slug}` | Get Post By Slug | 是 | - | - |
| DELETE | `/api/v1/community/posts/{post_id}` | Delete Post | 是 | - | - |
| GET | `/api/v1/community/posts/{post_id}` | Get Post | 是 | - | - |
| PUT | `/api/v1/community/posts/{post_id}` | Update Post | 是 | - | - |
| GET | `/api/v1/community/posts/{post_id}/comments` | List Comments | - | - | PaginatedResponse_dict_ |
| POST | `/api/v1/community/posts/{post_id}/comments` | Create Comment | 是 | - | - |
| POST | `/api/v1/community/reactions` | Toggle Like | 是 | - | - |
| POST | `/api/v1/community/reports` | Submit Report | 是 | - | - |
| GET | `/api/v1/community/series` | List Series | - | - | - |
| POST | `/api/v1/community/series` | Create Series | 是 | - | - |
| POST | `/api/v1/community/upload` | Upload Community Image | 是 | - | - |
| GET | `/api/v1/community/users/{user_id}/follow-counts` | Follow Counts | - | - | - |
| GET | `/api/v1/community/users/{user_id}/follow-status` | Follow Status | 是 | - | - |
| GET | `/api/v1/community/users/{user_id}/replies` | List User Replies | - | - | PaginatedResponse_dict_ |
| GET | `/api/v1/community/users/{user_id}/topics` | List User Topics | - | - | PaginatedResponse_dict_ |

## 管理员-活动

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/admin/events` | List All Events | 是 | - | EventListOut |
| POST | `/api/v1/admin/events` | Create Event | 是 | EventInput | - |
| POST | `/api/v1/admin/events/batch` | Batch Update Events | 是 | BatchUpdateRequest | - |
| DELETE | `/api/v1/admin/events/settings` | Reset Event Setting | 是 | - | - |
| GET | `/api/v1/admin/events/settings` | Get Event Settings | 是 | - | - |
| PUT | `/api/v1/admin/events/settings` | Update Event Settings | 是 | EventSettingsIn | - |
| GET | `/api/v1/admin/events/stats` | Event Stats | 是 | - | - |
| DELETE | `/api/v1/admin/events/{event_id}` | Delete Event | 是 | - | - |
| GET | `/api/v1/admin/events/{event_id}` | Get Event Detail | 是 | - | EventOut |
| PUT | `/api/v1/admin/events/{event_id}` | Update Event | 是 | EventInput | EventOut |
| POST | `/api/v1/admin/events/{event_id}/checkin` | Checkin By Code | 是 | - | - |
| POST | `/api/v1/admin/events/{event_id}/checkin/codes` | Generate Checkin Codes | 是 | - | - |
| GET | `/api/v1/admin/events/{event_id}/checkins` | List Checkins | 是 | - | - |
| GET | `/api/v1/admin/events/{event_id}/checkins/stats` | Checkin Stats | 是 | - | - |
| GET | `/api/v1/admin/events/{event_id}/registrations` | List Registrations | 是 | - | - |
| POST | `/api/v1/admin/events/{event_id}/registrations/manage` | Manage Registration | 是 | - | - |
| GET | `/api/v1/admin/events/{event_id}/registrations/stats` | Registration Stats | 是 | - | - |

## 管理员-用户管理

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/admin/users` | List Users | 是 | - | AdminUserListOut |
| DELETE | `/api/v1/admin/users/{user_id}` | Delete User Admin | 是 | - | - |
| GET | `/api/v1/admin/users/{user_id}` | Get User Detail | 是 | - | UserOut |
| PUT | `/api/v1/admin/users/{user_id}` | Update User Admin | 是 | AdminUserUpdate | AdminUserOut |
| POST | `/api/v1/admin/users/{user_id}/disable` | Disable User | 是 | - | AdminUserOut |
| POST | `/api/v1/admin/users/{user_id}/enable` | Enable User | 是 | - | AdminUserOut |
| POST | `/api/v1/admin/users/{user_id}/reset-password` | Reset Password Custom | 是 | - | - |
| POST | `/api/v1/admin/users/{user_id}/reset-password-default` | Reset Password Default | 是 | - | - |

## 管理员-社区

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/admin/community/categories` | Admin List Categories | 是 | - | - |
| POST | `/api/v1/admin/community/categories` | Create Category | 是 | - | - |
| DELETE | `/api/v1/admin/community/categories/{category_id}` | Delete Category | 是 | - | - |
| PUT | `/api/v1/admin/community/categories/{category_id}` | Update Category | 是 | - | - |
| DELETE | `/api/v1/admin/community/replies/{comment_id}` | Admin Hard Delete Comment | 是 | - | - |
| PUT | `/api/v1/admin/community/replies/{comment_id}` | Admin Update Comment | 是 | - | - |
| POST | `/api/v1/admin/community/replies/{comment_id}/hide` | Hide Comment | 是 | - | - |
| POST | `/api/v1/admin/community/replies/{comment_id}/restore` | Restore Comment | 是 | - | - |
| GET | `/api/v1/admin/community/reports` | List Reports | 是 | - | - |
| POST | `/api/v1/admin/community/reports/{report_id}/dismiss` | Dismiss Report | 是 | - | - |
| POST | `/api/v1/admin/community/reports/{report_id}/resolve` | Resolve Report | 是 | - | - |
| POST | `/api/v1/admin/community/series` | Admin Community Series Action | 是 | - | - |
| GET | `/api/v1/admin/community/topics` | Admin List Posts | 是 | - | - |
| DELETE | `/api/v1/admin/community/topics/{post_id}` | Admin Hard Delete Post | 是 | - | - |
| PUT | `/api/v1/admin/community/topics/{post_id}` | Admin Update Post | 是 | - | - |
| POST | `/api/v1/admin/community/topics/{post_id}/feature` | Feature Post | 是 | - | - |
| POST | `/api/v1/admin/community/topics/{post_id}/hide` | Hide Post | 是 | - | - |
| POST | `/api/v1/admin/community/topics/{post_id}/pin` | Pin Post | 是 | - | - |
| POST | `/api/v1/admin/community/topics/{post_id}/restore` | Restore Post | 是 | - | - |

## 管理员-角色权限

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/admin/permissions` | List Permissions | 是 | - | - |
| GET | `/api/v1/admin/roles` | List Roles | 是 | - | - |
| POST | `/api/v1/admin/roles` | Create Role | 是 | AdminRoleCreate | - |
| DELETE | `/api/v1/admin/roles/{role_id}` | Delete Role | 是 | - | - |
| PUT | `/api/v1/admin/roles/{role_id}` | Update Role | 是 | AdminRoleUpdate | AdminRoleOut |
| PUT | `/api/v1/admin/roles/{role_id}/permissions` | Replace Permissions | 是 | AdminRolePermissions | AdminRoleOut |

## 认证

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/auth/2fa` | Two Factor Status | 是 | - | TwoFactorStatusResponse |
| POST | `/api/v1/auth/2fa/backup-codes` | Two Factor Backup Codes | 是 | TwoFactorCodeRequest | - |
| POST | `/api/v1/auth/2fa/disable` | Two Factor Disable | 是 | TwoFactorCodeRequest | - |
| POST | `/api/v1/auth/2fa/setup` | Two Factor Setup | 是 | - | TwoFactorSetupResponse |
| POST | `/api/v1/auth/2fa/verify` | Two Factor Verify | 是 | TwoFactorVerifyRequest | LoginResponse |
| POST | `/api/v1/auth/forgot-password` | Forgot Password | - | ForgotPasswordRequest | - |
| POST | `/api/v1/auth/login` | Login | - | - | TokenPair |
| POST | `/api/v1/auth/login-email` | Login Email | - | EmailLoginRequest | LoginResponse |
| POST | `/api/v1/auth/login-json` | Login Json | - | LoginRequest | TokenPair |
| POST | `/api/v1/auth/logout` | Logout | 是 | - | - |
| GET | `/api/v1/auth/me` | Read Users Me | 是 | - | MeResponse |
| GET | `/api/v1/auth/oauth/github` | Oauth Github Entry | - | - | - |
| GET | `/api/v1/auth/oauth/github/callback` | Oauth Github Callback | - | - | LoginResponse |
| POST | `/api/v1/auth/refresh` | Refresh Token | - | RefreshRequest | TokenPair |
| POST | `/api/v1/auth/register` | Register | - | RegisterRequest | LoginResponse |
| POST | `/api/v1/auth/send-code` | Send Code | - | SendCodeRequest | - |
| GET | `/api/v1/auth/sessions` | List Sessions | 是 | - | SessionListResponse |
| DELETE | `/api/v1/auth/sessions/{token_id}` | Delete Session | 是 | - | - |

## 通知

| 方法 | 路径 | 说明 | 认证 | 请求体 | 成功响应 |
|---|---|---|---|---|---|
| GET | `/api/v1/notifications` | List Notifications | 是 | - | PaginatedResponse_NotificationOut_ |
| POST | `/api/v1/notifications/broadcast` | Broadcast | 是 | BroadcastRequest | - |
| GET | `/api/v1/notifications/broadcast-history` | Broadcast History | 是 | - | - |
| POST | `/api/v1/notifications/read-all` | Mark All Read | 是 | - | - |
| GET | `/api/v1/notifications/unread-count` | Unread Count | 是 | - | - |
| POST | `/api/v1/notifications/{notification_id}/read` | Mark Read | 是 | - | - |

---

## Schemas（components.schemas）

- `ActivityParticipationOut`
- `AdminPermissionOut`
- `AdminRoleCreate`
- `AdminRoleOut`
- `AdminRolePermissions`
- `AdminRoleUpdate`
- `AdminUserListOut`
- `AdminUserOut`
- `AdminUserUpdate`
- `AnnouncementInput`
- `AnnouncementOut`
- `ApiUsageDay`
- `ApiUsageEndpoint`
- `ApiUsageStats`
- `ApiUsageToday`
- `AuditLogItem`
- `AuxilioChatEvent`
- `AvatarPresetRequest`
- `BatchUpdateRequest`
- `Body_login_api_v1_auth_login_post`
- `Body_upload_avatar_api_v1_profile_avatar_upload_post`
- `Body_upload_community_image_api_v1_community_upload_post`
- `Body_upload_resource_file_api_v1_tools_resource_upload_post`
- `BroadcastRequest`
- `ChangePasswordRequest`
- `ChatMessageListOut`
- `ChatMessageOut`
- `ChatRequest`
- `ChatTurn`
- `ComponentGuideInput`
- `ComponentItemInput`
- `ComponentVariantInput`
- `ConversationListOut`
- `ConversationOut`
- `CreateAuditLogRequest`
- `EmailLoginRequest`
- `EventCheckinOut`
- `EventInput`
- `EventListOut`
- `EventOut`
- `EventRegistrationInput`
- `EventRegistrationOut`
- `EventSettingsIn`
- `ExamAttemptInput`
- `ExamInput`
- `ExamSubmitIn`
- `ExceptionLogItem`
- `ExceptionLogResolveResponse`
- `FocusSessionIn`
- `FocusSessionOut`
- `ForgotPasswordRequest`
- `GithubContributionsOut`
- `GithubDayCount`
- `HTTPValidationError`
- `JoinApplicationInput`
- `JoinApplicationOut`
- `JoinReviewRequest`
- `LlmConfigIn`
- `LlmConfigOut`
- `LlmConfigUpdateOut`
- `LlmUsageDay`
- `LlmUsageModel`
- `LlmUsageStats`
- `LlmUsageToday`
- `LoginRequest`
- `LoginResponse`
- `MeResponse`
- `NotificationOut`
- `PaginatedResponse_AuditLogItem_`
- `PaginatedResponse_EventOut_`
- `PaginatedResponse_ExceptionLogItem_`
- `PaginatedResponse_NotificationOut_`
- `PaginatedResponse_Permission_`
- `PaginatedResponse_Role_`
- `PaginatedResponse_User_`
- `PaginatedResponse_dict_`
- `Permission`
- `PermissionCreate`
- `PermissionUpdate`
- `PomodoroDay`
- `PomodoroStats`
- `ProfileResponse`
- `ProfileUpdate`
- `PublicUserOut`
- `PublicUserProfileResponse`
- `QuestionInput`
- `RefreshRequest`
- `RegisterRequest`
- `RegistrationField`
- `ResetRequestOut`
- `ResetRequestResolve`
- `ResourceInput`
- `Role`
- `RoleCreate`
- `RoleUpdate`
- `SendCodeRequest`
- `SessionListResponse`
- `SessionOut`
- `TaskInput`
- `TokenPair`
- `ToolCallOut`
- `TwoFactorCodeRequest`
- `TwoFactorSetupResponse`
- `TwoFactorStatusResponse`
- `TwoFactorVerifyRequest`
- `User`
- `UserCreate`
- `UserOut`
- `UserPermissionCheck`
- `UserPermissionResult`
- `UserPermissionsResponse`
- `UserUpdate`
- `ValidationError`
