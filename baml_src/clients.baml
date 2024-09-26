// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview
retry_policy AExpRetryPolicy {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 200
    multiplier 2.5
    max_delay_ms 10000
  }
}

client<llm> AFallbackClient {
  retry_policy AExpRetryPolicy
  provider fallback
  options {
    strategy [
      QwenPlusLatest
      QwenPlus
    ]
  }
}


client<llm> QwenPlusLatest {
  provider "openai-generic"
  options {
    base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model "qwen-plus-latest"
    api_key env.QWEN_API_KEY
    default_role "user"
  }
}

client<llm> QwenPlus {
  provider "openai-generic"
  options {
    base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model "qwen-plus"
    api_key env.QWEN_API_KEY
    default_role "user"
  }
}

client<llm> LLaMa3_2_3B {
  provider "openai-generic"
  options {
    base_url "http://localhost:11434/v1"
    model "llama3.2"
  }
}

client<llm> GPT4o {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> GPT4oMini {
  provider openai
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> Sonnet {
  provider anthropic
  options {
    model "claude-3-5-sonnet-20240620"
    api_key env.ANTHROPIC_API_KEY
  }
}


client<llm> Haiku {
  provider anthropic
  options {
    model "claude-3-haiku-20240307"
    api_key env.ANTHROPIC_API_KEY
  }
}

client<llm> Fast {
  provider round-robin
  options {
    // This will alternate between the two clients
    strategy [GPT4oMini, Haiku]
  }
}

client<llm> Openai {
  provider fallback
  options {
    // This will try the clients in order until one succeeds
    strategy [GPT4o, GPT4oMini]
  }
}