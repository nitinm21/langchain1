# What Would They Say? 

Ever wondered what Steve Jobs would tell you about your startup idea? Or what Kobe Bryant would say about your work ethic? Or how Marcus Aurelius would stoically judge your life choices?

Well, now you can fafo! 

## What is this?

It's basically a Magic 8-Ball, except instead of vague fortunes, you get life advice from dead famous people. Also, it's a demo showcasing **LangChain** for building RAG (Retrieval-Augmented Generation) pipelines and personality-driven chatbots. 

Chat with:
- **Steve Jobs** - He'll tell you why your design sucks (but like, nicely)
- **Kobe Bryant** - Prepare for a lecture on your "Mamba Mentality" 
- **Marcus Aurelius** - Roman emperor who'll make you feel bad about complaining... philosophically

## How do I run this thing?

First, you'll need Python. If you don't have Python installed... well, that's a different README.

### Step 1: Install the stuff

```bash
pip install -r requirements.txt
```

This includes all the LangChain goodies (langchain, langchain-openai, langchain-community) for building the RAG pipeline, plus Flask for the web interface. Basically, everything you need to make dead people talk.


### Step 2: Set up your environment

Create a `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your_key_here
```



### Step 3: Run it!

```bash
python app.py
```

Then open your browser and go to: `http://127.0.0.1:5000`

That's it! You're now ready to receive wisdom from beyond the grave. Or at least from a language model pretending to be beyond the grave.

---

Built with **LangChain**, Python, Flask, and questionable life decisions.
