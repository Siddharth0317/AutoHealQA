import logging
from typing import Dict, Any, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class DOMInspector:
    """
    Utility for extracting DOM snapshot details, element hierarchy,
    and contextual outer HTML when a Playwright locator fails.
    """

    @staticmethod
    async def capture_failure_context(
        page: Page,
        failed_selector: str,
        target_description: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Extracts DOM hierarchy, candidate interactable elements, and page metadata.
        """
        context = {
            "url": page.url,
            "title": await page.title(),
            "failed_selector": failed_selector,
            "target_description": target_description,
            "action": action,
            "dom_snippet": "",
            "interactable_elements": []
        }

        try:
            # Script to extract interactive elements and body snippet
            eval_script = """
            () => {
                const getCleanSnippet = () => {
                    const mainEl = document.querySelector('main, form, #app, .container') || document.body;
                    let clone = mainEl.cloneNode(true);
                    // Strip out script and style tags to keep prompt compact
                    const scripts = clone.querySelectorAll('script, style, svg, iframe');
                    scripts.forEach(s => s.remove());
                    let html = clone.outerHTML;
                    if (html.length > 5000) {
                        html = html.substring(0, 5000) + '... [TRUNCATED]';
                    }
                    return html;
                };

                const getInteractables = () => {
                    const elements = Array.from(document.querySelectorAll('button, input, a, select, textarea, [role="button"], [data-testid]'));
                    return elements.slice(0, 25).map(el => ({
                        tag: el.tagName.toLowerCase(),
                        id: el.id || null,
                        name: el.name || null,
                        type: el.getAttribute('type') || null,
                        placeholder: el.getAttribute('placeholder') || null,
                        text: (el.textContent || '').trim().substring(0, 40),
                        dataTestId: el.getAttribute('data-testid') || el.getAttribute('data-test') || null,
                        class: el.className || null,
                        ariaLabel: el.getAttribute('aria-label') || null
                    }));
                };

                return {
                    snippet: getCleanSnippet(),
                    interactables: getInteractables()
                };
            }
            """
            result = await page.evaluate(eval_script)
            context["dom_snippet"] = result.get("snippet", "")
            context["interactable_elements"] = result.get("interactables", [])

        except Exception as e:
            logger.warning(f"Error extracting DOM context from page: {e}")
            try:
                content = await page.content()
                context["dom_snippet"] = content[:3000]
            except Exception:
                context["dom_snippet"] = "<body>Could not capture DOM content</body>"

        return context
