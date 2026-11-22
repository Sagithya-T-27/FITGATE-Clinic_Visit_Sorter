# FITGATE – Project Reflection

Developing FITGATE helped me understand how an LLM can be used as part of a practical application while keeping important safety decisions under Python control. The project focuses on a factory clinic where workers arrive during short breaks and may be seen in arrival order. I wanted to create a tool that helps the nurse identify workers who may require earlier attention, especially when their symptoms affect their job.

One important decision was using an LLM to classify informal worker notes. Workers may describe their symptoms in English, Tamil or Tanglish, so a language model can help interpret different ways of expressing the same problem. However, I learned that the LLM should not be trusted without checking its output. This is why I created a JSON validation function and included a retry mechanism.

Another important learning was the difference between AI decisions and Python decisions. The LLM identifies symptoms and affected abilities, while Python checks the job-needs mapping and red-flag phrases. For example, blurry vision may create a different workplace safety concern for a welder or driver. Keeping this mapping in Python makes the rules more consistent and easier to inspect.

I also learned why a priority that is too low can be more dangerous than one that is too high. A worker with chest pain or difficulty breathing should not remain behind less urgent cases simply because the LLM makes a mistake. Therefore, I implemented a raise-only priority rule. The application also uses a safe fallback when the API fails or returns invalid information.

Testing was an important part of the project. The evaluation harness checks five normal inputs, while red-team testing examines requests to ignore instructions, requests for diagnoses and Tamil/Tanglish red-flag notes. These tests help identify weaknesses rather than assuming that a program is correct because it runs.

One of the main challenges was ensuring that all workers remain in the queue, including duplicate IDs and records with unreadable times. I also had to separate the nurse's detailed report from the in-charge's summary to protect worker information.

Overall, this project taught me that an LLM application needs more than a good prompt. It needs validation, independent safety rules, testing, privacy protection and human oversight. FITGATE only organises the queue and displays possible job-related risks. The nurse remains responsible for reviewing every worker and making all medical decisions.
