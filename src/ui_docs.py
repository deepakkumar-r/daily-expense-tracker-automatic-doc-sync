"""Static frontend inventory rendering; never import or execute documented assets."""

from __future__ import annotations

import hashlib
import html
from html.parser import HTMLParser
import re
from urllib.parse import quote

MARKER = "<!-- docsync:generated:v1 -->\n"
SUFFIXES = (".html", ".css", ".js")


class PageInventory(HTMLParser):
    """Collect explicit HTML metadata, components, controls and local assets."""

    def __init__(self) -> None:
        """Initialize an empty semantic page inventory."""
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.description = "Not Found"
        self.components: list[tuple[str, str]] = []
        self.controls: list[tuple[str, str, str]] = []
        self.assets: set[str] = set()
        self.headings: list[str] = []
        self._capture: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Read only allowlisted publishable metadata, not arbitrary field values."""
        attributes = dict(attrs)
        if tag in ("title", "h1", "h2", "h3"):
            self._capture = tag
            self._text = []
        if tag == "meta" and attributes.get("name") == "description":
            self.description = attributes.get("content") or "Not Found"
        if attributes.get("data-component"):
            self.components.append((attributes["data-component"] or "", attributes.get("data-doc") or "Not Found"))
        if tag in ("form", "input", "select", "textarea", "button", "dialog"):
            self.controls.append((
                tag, attributes.get("id") or attributes.get("name") or "Not Found",
                attributes.get("type") or attributes.get("aria-label") or "Not Found",
            ))
        if tag in ("script", "link"):
            target = attributes.get("src" if tag == "script" else "href")
            if target:
                self.assets.add(target)

    def handle_data(self, data: str) -> None:
        """Capture visible title and heading text."""
        if self._capture:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        """Finalize text of the currently captured title or heading."""
        if tag == self._capture:
            text = " ".join("".join(self._text).split())
            if tag == "title":
                self.title.append(text)
            elif text:
                self.headings.append(text)
            self._capture = None


def masked_source(text: str, javascript: bool = False) -> str:
    """Mask comments and strings for a conservative declaration-only inventory."""
    pattern = r'/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    if javascript:
        pattern += r"|`(?:\\.|[^`\\])*`|//[^\n]*"
    return re.sub(pattern, lambda match: re.sub(r"[^\n]", " ", match.group()), text)


def render_ui(files: dict[str, bytes]) -> str:
    """Render deterministic frontend structure, explicit descriptions and raw-byte fingerprint."""
    digest = hashlib.sha256()
    sections: list[str] = []

    def code(text: str) -> str:
        return "<code>" + html.escape(text) + "</code>"

    def prose(text: str) -> str:
        return "<pre>" + html.escape(text) + "</pre>"

    for name, content in sorted(files.items()):
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(len(content).to_bytes(8, "big") + content)
        text = content.decode("utf-8-sig")
        sections.extend([f"## {code(name)}\n", f"[Source](../{quote(name, safe='/')})\n"])
        if name.endswith(".html"):
            page = PageInventory()
            page.feed(text)
            page.close()
            sections.extend(["### Page\n", prose(" ".join(page.title) or "Not Found"),
                             prose(page.description), "\n### Headings\n"])
            sections.extend("- " + code(heading) for heading in page.headings)
            sections.append("\n### Components and functionality\n")
            if not page.components:
                sections.append("Not Found")
            for label, description in page.components:
                sections.extend(["#### " + code(label), prose(description)])
            sections.append("\n### Controls\n")
            sections.extend("- " + code(f"{tag} #{identifier}: {kind}") for tag, identifier, kind in page.controls)
            sections.append("\n### Linked assets\n")
            sections.extend("- " + code(asset) for asset in sorted(page.assets))
        elif name.endswith(".css"):
            clean = masked_source(text)
            selectors = sorted({
                match.strip() for match in re.findall(r"([^{};]+)\{", clean)
                if match.strip()
            })
            sections.append("### Style selectors and responsive rules\n")
            sections.extend("- " + code(selector) for selector in selectors)
            if not selectors:
                sections.append("Not Found")
        else:
            clean = masked_source(text, javascript=True)
            functions = set(re.findall(r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", clean))
            functions.update(re.findall(
                r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
                clean,
            ))
            classes = set(re.findall(r"\bclass\s+([A-Za-z_$][\w$]*)", clean))
            sections.append("### Named functions and classes\n")
            sections.extend("- " + code(label) for label in sorted(functions | classes))
            if not functions and not classes:
                sections.append("Not Found")
            sections.append("\n### Explicit functionality descriptions\n")
            descriptions = re.findall(r"/\*\*\s*@ui\s+([\s\S]*?)\*/", text)
            sections.extend(prose(" ".join(description.split())) for description in descriptions)
            if not descriptions:
                sections.append("Not Found")
        sections.append("")
    return (
        MARKER + "# Frontend UI reference\n\n"
        + "Generated from HTML, CSS and JavaScript; do not edit manually.\n\n"
        + "Static inventory, not runtime inference or a full CSS/JavaScript syntax validator. "
        + "Functionality comes from HTML data-doc and JavaScript @ui comments. "
        + "Missing descriptions are Not Found. Raw source and field values are not published.\n\n"
        + f"Source fingerprint: `{digest.hexdigest()}`\n\n"
        + ("\n".join(sections) if files else "Frontend pages, components and functionality: Not Found.\n")
    )
