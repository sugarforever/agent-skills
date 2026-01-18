# Common Terminology Reference

This reference contains frequently encountered speech recognition errors and their corrections, organized by domain.

## AI/ML Frameworks and Tools

### LangChain Ecosystem
| Speech Recognition Error | Correct Term |
|-------------------------|--------------|
| 蓝犬 | LangChain |
| 蓝卷 | LangChain |
| Lantern | LangChain |
| Luncheon | langchain |
| lunch | langchain |
| learning | LangChain |
| land GRAPH | langgraph |
| LAN GRAPH | langgraph |
| Linux (in context) | LangGraph |
| a memory Server | MemorySaver |
| AMM Server | MemorySaver |
| amneserver | MemorySaver |
| check point | checkpointer |
| Sharepoint | checkpointer |

### OpenAI
| Speech Recognition Error | Correct Term |
|-------------------------|--------------|
| open EI | OpenAI |
| open Email | OpenAI |
| open AI | OpenAI |
| GPT store Mini | gpt-4o-mini |

### General AI Terms
| Speech Recognition Error | Correct Term |
|-------------------------|--------------|
| 拖 | tool |
| tour | tool |
| 拖run time | ToolRuntime |
| wrong time | runtime |
| TOKEN (in wrong context) | tool |
| GE组件 | 记忆组件 |

## Chinese Phonetic Errors (同音字)

### Common Pairs
| Error | Correction | Pinyin |
|-------|------------|--------|
| 绘画 | 会话 | huìhuà |
| 源数据 | 元数据 | yuán shùjù |
| 本科 | 本课 | běnkè |
| 事例 | 示例 | shìlì |
| 时间代码 | 实践代码 | shíjiàn |
| 详细的裁剪 | 消息的裁剪 | xiāoxi |
| 中间键 | 中间件 | zhōngjiànjiàn |
| 大约模型 | 大模型 | dà móxíng |
| 希望到 | 希望得到 | xīwàng dédào |
| 名字空间 | 命名空间 | mìngmíng kōngjiān |
| 流逝 | 流式 | liúshì |
| 约着 | 约定 | yuēdìng |

## Code-Related Corrections

### Variable/Function Naming Conventions
| Spoken Form | Written Form |
|-------------|--------------|
| user underscore 001 | user_001 |
| thread underscore id | thread_id |
| user underscore level | user_level |
| create underscore agent | create_agent |
| trim underscore messages | trim_messages |
| before underscore model | before_model |
| remove underscore all underscore messages | remove_all_messages |

### Method Calls
| Spoken Form | Written Form |
|-------------|--------------|
| runtime点state | runtime.state |
| runtime点context | runtime.context |
| agent点invoke | agent.invoke |
| result点get | result.get |

### Class Names
| Error | Correction |
|-------|------------|
| agent state | AgentState |
| custom state | CustomState |
| user context | UserContext |
| task manager state | TaskManagerState |
| tool message | ToolMessage |
| remove message | RemoveMessage |

## API Configuration Terms

### Config/Configurable
| Error | Correction |
|-------|------------|
| confict | config |
| conflict | config |
| THREAD ID | thread_id |
| context schemer | context_schema |
| state schemer | state_schema |
| text meta data | tags metadata |

## Domain-Specific: Video Course Content

### Course Structure Terms
| Error | Correction |
|-------|------------|
| 第X科 | 第X课 |
| 本科 | 本课 |
| 向消息 | 消息 |

### Presenter Names (Context-Specific)
When users provide specific names in their terminology list:
- These are likely presenter or speaker names
- Should be preserved exactly as provided
- Use as reference for identifying speech recognition errors

## Usage Notes

1. **Context Matters**: Many errors depend on context
   - "TOKEN" might be correct in "token数" but wrong in "TOKEN ID" (should be "tool ID")
   - "客户" vs "客服" depends on who is speaking

2. **Consistency**: Once a correction is identified, apply it consistently throughout

3. **Compound Errors**: Watch for multiple errors in one term
   - "Luncheon open EI" → "langchain-openai"
   - "open AI underscore API underscore key" → "OPENAI_API_KEY"

4. **Case Sensitivity**:
   - Package names: lowercase (langchain, langgraph)
   - Class names: PascalCase (LangChain, MemorySaver)
   - Environment variables: UPPER_SNAKE_CASE
