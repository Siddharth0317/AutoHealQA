import logging
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from agents.groq_client import groq_client

logger = logging.getLogger(__name__)


class HealedSelectorResponse(BaseModel):
    original_selector: str = Field(..., description="The selector that failed")
    healed_selector: str = Field(..., description="The repaired primary CSS or XPath selector")
    fallback_selector: Optional[str] = Field(None, description="Secondary fallback locator")
    reasoning: str = Field(..., description="Explanation of why repair was made")
    confidence_score: float = Field(..., description="Confidence score between 0.0 and 1.0")


SYSTEM_PROMPT = """
You are an Autonomous Self-Healing Test Automation AI Specialist.
A Playwright browser test encountered an element lookup failure during execution.

Your objective:
Analyze the failed selector, target description, error message, and DOM snapshot/interactable elements array, and generate an alternative, robust repair selector.

Priority locator strategies:
1. `[data-testid="..."]` or `[data-test="..."]`
2. Element ID or exact Name attribute (`#id`, `input[name="..."]`)
3. Accessible attributes (`[aria-label="..."]`, `[placeholder="..."]`)
4. Text locators (`text="Button Text"` or `button:has-text("Submit")`)
5. Specific relative CSS selector or XPath (`//button[contains(text(), "...")]`)

You MUST respond strictly with a valid JSON object matching this schema:
{
  "original_selector": "#failed-selector",
  "healed_selector": "button[type='submit']",
  "fallback_selector": "text='Submit'",
  "reasoning": "Original selector #failed-selector was missing. Target button matches button[type='submit'] in DOM snippet.",
  "confidence_score": 0.95
}
"""


class SelfHealingAgent:
    """
    AI Agent that inspects broken DOM contexts and generates replacement selectors.
    """

    def __init__(self):
        self.client = groq_client

    async def heal_selector(
        self,
        failed_selector: str,
        target_description: str,
        action: str,
        error_message: str,
        dom_context: Dict[str, Any]
    ) -> HealedSelectorResponse:
        """
        Sends failure context to Groq LLM and returns a repaired selector.
        """
        logger.info(f"Attempting self-healing for failed selector: '{failed_selector}'")

        user_prompt = f"""
Execution Failure Details:
- Action Attempted: {action}
- Target Description: {target_description}
- Failed Selector: {failed_selector}
- Error Message: {error_message}
- Current Page URL: {dom_context.get('url', 'Unknown')}
- Current Page Title: {dom_context.get('title', 'Unknown')}

Candidate Interactable Elements in DOM:
{json.dumps(dom_context.get('interactable_elements', []), indent=2)}

DOM HTML Snippet:
{dom_context.get('dom_snippet', '')[:2500]}
"""

        # Generate intelligent mock fallback if in mock mode
        mock_healed = self._generate_mock_healing(failed_selector, target_description, action, dom_context)

        mock_payload = {
            "original_selector": failed_selector,
            "healed_selector": mock_healed["primary"],
            "fallback_selector": mock_healed["fallback"],
            "reasoning": f"Auto-detected candidate matching '{target_description}' from DOM interactables list.",
            "confidence_score": 0.90
        }

        completion_res = await self.client.generate_chat_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
            json_mode=True,
            mock_fallback_response=mock_payload
        )

        parsed = completion_res.get("parsed") or mock_payload

        return HealedSelectorResponse(
            original_selector=failed_selector,
            healed_selector=parsed.get("healed_selector") or mock_healed["primary"],
            fallback_selector=parsed.get("fallback_selector") or mock_healed["fallback"],
            reasoning=parsed.get("reasoning", "Selector auto-repaired by LLM agent."),
            confidence_score=float(parsed.get("confidence_score", 0.85))
        )

    def _generate_mock_healing(
        self,
        failed_selector: str,
        target_description: str,
        action: str,
        dom_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Derives fallback repair selectors from interactable elements array if available.
        """
        interactables = dom_context.get("interactables", [])
        desc_lower = target_description.lower()

        for el in interactables:
            text = (el.get("text") or "").lower()
            aria = (el.get("ariaLabel") or "").lower()
            name = (el.get("name") or "").lower()
            tid = el.get("dataTestId")

            if tid:
                return {"primary": f"[data-testid='{tid}']", "fallback": f"text='{el.get('text')}'"}
            if desc_lower in text or text in desc_lower:
                tag = el.get("tag", "button")
                return {"primary": f"{tag}:has-text('{el.get('text')}')", "fallback": f"text='{el.get('text')}'"}
            if name and name in desc_lower:
                return {"primary": f"[name='{el.get('name')}']", "fallback": f"#{el.get('id')}" if el.get("id") else None}

        # General default fallback strategies
        if "login" in desc_lower or "submit" in desc_lower or "sign in" in desc_lower:
            return {"primary": "button[type='submit'], button:has-text('Sign'), text='Log In'", "fallback": "button"}
        if "user" in desc_lower or "email" in desc_lower:
            return {"primary": "input[type='email'], input[name='username'], input[name='email']", "fallback": "input"}
        if "pass" in desc_lower:
            return {"primary": "input[type='password'], input[name='password']", "fallback": "input[type='password']"}

        return {"primary": "body", "fallback": "html"}


# Singleton instance
self_healing_agent = SelfHealingAgent()
