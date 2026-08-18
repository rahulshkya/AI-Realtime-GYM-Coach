from services.config.workout_config import PROMPT

class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT

    def give_feedback(self, event, issue):
        print(f"LLM CALLED -> Event: {event}, Issue: {issue}")

        # Pehle prompt banao
        prompt = f"EVENT: {event}"

        if issue:
            prompt += f"\nISSUE: {issue}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            reasoning_effort="low",   # reasoning kam karega
            max_completion_tokens=160,
            temperature=0.5
        )

        msg = response.choices[0].message

        text = msg.content
        if not text:
            text = msg.reasoning

        print(response)
        print("Finish:", response.choices[0].finish_reason)
        print("Content repr:", repr(response.choices[0].message.content))
       

        # Ab history save karo
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": text})

        print("LLM RESPONSE:", text)

        return text