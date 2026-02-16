# Vendoring Patterns

This directory contains example patterns from community members who have vendored Tantra and customized it for their needs.

## Contributing Your Pattern

Vendored Tantra and made a useful customization? Share it here!

### How to Share

1. Extract your modification as a standalone example
2. Document what it does and why
3. Submit a PR to add it to this directory
4. **Keep your vendored code** - you're just sharing the pattern!

## Example Patterns

(Coming soon as community shares their customizations)

### Ideas for Patterns

- **Custom Rate Limiting**: Add rate limiting to providers
- **Advanced Logging**: Structured logging with context
- **Retry Logic**: Exponential backoff implementations
- **Metrics Integration**: Prometheus, DataDog, etc.
- **Custom Providers**: Ollama, local models, etc.
- **Streaming Implementations**: Real-time response handling
- **Token Budget Management**: Stay within cost limits
- **Custom Tool Validators**: Validate tool inputs/outputs
- **Multi-Tenant Support**: User isolation in agents
- **Caching Layer**: Cache LLM responses

## Pattern Format

When contributing, include:

```
pattern_name/
├── README.md          # What it does, why, how to use
├── example.py         # Working example
└── modifications.md   # Specific files/functions changed
```

## Guidelines

- **Self-contained**: Pattern should be easy to understand and apply
- **Well-documented**: Explain the why, not just the what
- **Tested**: Include example showing it works
- **Generalizable**: Useful for others, not hyper-specific

---

**Share your vendoring customizations and help the community!** 🚀
