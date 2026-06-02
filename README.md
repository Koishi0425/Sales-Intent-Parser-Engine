# Sales Intent Parser Engine

企业级 B2B 销售需求意图解析后端服务。项目把销售侧口语化、碎片化的客户反馈转换为标准结构化数据，再通过规则引擎自动进入对应业务分支。

核心目标：

- 解析自然语言需求：例如“大概 10 个人”“想先试一个月”“要固定公网 IP”。
- 推理业务字段：例如按“每人 1 Mbps”估算办公带宽。
- 自动路由：海外访问、国内组网、固定 IP/大带宽、需求澄清。
- 对接下游：返回报价草案、负责人团队、CRM payload 和下一步动作。

## 架构

```text
Input API / CLI
  -> Intention Parser
      -> LLM Structured Output
      -> Local Heuristic Fallback
  -> Pydantic Validator
  -> Rule Engine
  -> Action Executor
  -> WorkflowResult
```

模块说明：

- `src/intent_parser/models.py`：Pydantic 数据模型，定义需求、路由决策和动作结果。
- `src/intent_parser/parsers.py`：智能解析层，优先调用 OpenAI-compatible API，未配置密钥时使用本地启发式解析。
- `src/intent_parser/rules.py`：规则引擎，基于结构化字段做业务分支判断。
- `src/intent_parser/actions.py`：业务执行层，生成报价草案、CRM payload 和下一步动作。
- `src/intent_parser/api.py`：FastAPI 服务入口。
- `src/intent_parser/cli.py`：命令行演示入口。

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

如果只想运行核心逻辑，至少需要安装：

```bash
python -m pip install pydantic
```

## 配置 LLM

复制 `.env.example` 后配置环境变量。未配置密钥时，项目会自动使用本地启发式解析，适合测试和演示。

```bash
set LLM_API_KEY=your-api-key
set LLM_MODEL=gpt-4o-mini
set LLM_BASE_URL=
set LLM_ENABLE_THINKING=false
set LLM_ENABLE_SEARCH=
set LLM_CACHE_CONTROL=
set LLM_TEMPERATURE=0
set LLM_MAX_TOKENS=300
set LLM_TIMEOUT_SECONDS=60
```

如果使用 Qwen 或其他 OpenAI-compatible API，可设置：

```bash
set LLM_BASE_URL=https://your-compatible-endpoint/v1
set LLM_MODEL=your-model-name
```

对结构化抽取任务，建议关闭模型思考并限制输出长度：

- `LLM_ENABLE_THINKING=false`：对 Qwen/DashScope 这类支持 thinking 的模型关闭思考模式。
- `LLM_ENABLE_SEARCH=false`：对 DashScope/Qwen 明确关闭联网搜索，避免额外检索延迟。
- `LLM_CACHE_CONTROL=ephemeral`：可选。对 DashScope 显式缓存固定 prompt；只有固定前缀较长时更有价值，短 prompt 可保持为空。
- `LLM_TEMPERATURE=0`：降低输出发散，提升 JSON 稳定性。
- `LLM_MAX_TOKENS=300`：限制解析结果长度，避免不必要的输出成本。
- `LLM_TIMEOUT_SECONDS=60`：控制单次模型请求最长等待时间。

业务默认值：

```bash
set PER_USER_BANDWIDTH_MBPS=1
set HIGH_BANDWIDTH_THRESHOLD_MBPS=100
```

## 启动 API

```bash
uvicorn intent_parser.api:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://localhost:8000/health
```

分析需求：

```bash
curl -X POST http://localhost:8000/analyze_demand ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"客户上海办公室大概10个人，想先试一个月访问美国 SaaS，预算5000左右。\"}"
```

示例返回中的关键字段：

```json
{
  "structured_data": {
    "access_source": "上海办公室",
    "target_region": "美国",
    "user_count": 10,
    "bandwidth_est_mbps": 10,
    "duration": "试用1个月",
    "budget": 5000,
    "scenario_type": "overseas_access"
  },
  "decision": {
    "route": "flow_overseas_access",
    "action": "执行：访问海外应用子流程"
  },
  "action_result": {
    "owner_team": "海外访问技术组"
  }
}
```

## 命令行演示

```bash
python -m intent_parser.cli "深圳和广州两个点要内网互通，150人办公，先按半年看。"
```

## 路由规则

当前规则优先级：

1. 固定 IP / 公网 IP / 专线 / 带宽超过阈值：`flow_dedicated_ip_bandwidth`
2. 国内来源访问海外目标：`flow_overseas_access`
3. 国内站点互通或多点组网：`flow_domestic_networking`
4. 字段不足：`flow_clarify_requirements`

## 测试

使用标准库测试：

```bash
python -m unittest discover -s tests
```

安装 dev 依赖后也可以使用：

```bash
pytest
```
