# Azure Semantic Kernel

This Jupyter Notebook is a hands-on example demonstrating the core functionalities of the Azure Semantic Kernel. It showcases how to set up the kernel, integrate a chat completion service, and create custom plugins to extend the kernel's capabilities.

## 📝 About This Notebook

The notebook walks through the following key concepts:

  * **Kernel Initialization**: Sets up the Semantic Kernel.
  * **Chat Service Integration**: Connects to a powerful language model to enable conversational AI.
  * **Custom Plugin Creation**: Defines a `LightsPlugin` with functions to get the status of lights, change their state, and add new lights to a system.
  * **Function Calling**: The AI dynamically calls functions from the `LightsPlugin` based on the user's natural language commands. For instance, when asked to "Turn on the Porch light," the kernel intelligently executes the `change_state` function with the correct parameters.
  * **Extending Functionality**: The notebook demonstrates how the AI initially fails to add a new light because the function doesn't exist, and then succeeds after the `add_light` function is added to the plugin, showcasing the kernel's ability to adapt to new tools.

## 🔑 API Key and Model Configuration

This example uses the **Google Gemini Pro** model for chat completion. You will need to provide your own `GOOGLE_API_KEY` in a `.env` file for the notebook to run successfully.

While this notebook is configured for Gemini, the Azure Semantic Kernel is highly flexible. You can easily switch to other services like Azure OpenAI, OpenAI, or Hugging Face by changing the connector.

## 🚀 Using Other Chatbot Services

To configure the kernel with a different chat completion service, you can follow the official documentation provided by Microsoft. This guide contains detailed instructions and code samples for various models.

  * **Official Documentation**: [Add a chat completion service to your kernel](https://learn.microsoft.com/en-us/semantic-kernel/concepts/ai-services/chat-completion/?tabs=csharp-AzureOpenAI%2Cpython-Google%2Cjava-AzureOpenAI&pivots=programming-language-python)