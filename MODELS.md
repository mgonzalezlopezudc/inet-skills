# Specialist model classes

This is an overview of model bindings for the semantic specialist classes. Classes describe the
kind of work, so different classes may intentionally share a model binding. The platform runner
configuration is authoritative when a binding differs from this table.

| Class | Codex | Antigravity | Kimi |
| --- | --- | --- | --- |
| Extraction | GPT-5.6 Luna, high | Gemini 3.8 Flash, low | Kimi K3, low |
| Implementation | GPT-5.6 Luna, max | Gemini 3.8 Flash, medium | Kimi K3, high |
| Navigation | GPT-5.6 Luna, max | Gemini 3.8 Flash, medium | Kimi K3, high |
| Reasoning | GPT-5.6 Sol, xhigh | Gemini 3.8 Flash, high | Kimi K3, max |
