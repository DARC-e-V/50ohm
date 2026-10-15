/**
 * Moves the margin boxes into the margin column, or back into the text flow.
 *
 * Port of the inline script in ohm_renderer/templates/margin.html. That template rendered one
 * script per box, with the ids of the box, of its original position and of the `---` anchor it
 * belongs to baked in. The MDX only carries `<Tag type="…">`, so the pairing is derived here:
 * the original position is the `<a class="margin-origin">` right behind the box, and the anchor
 * is the nearest `<a id="margin_N">` in front of it.
 */

const ANCHOR_ID = /^margin_\d+$/;
const WIDE_FROM = 800;

interface Box {
  element: HTMLElement;
  /** Where the box sits in the text flow. */
  origin: Element;
  /** Where it goes in the margin column. */
  anchor: Element | null;
}

function collect(): Box[] {
  // Both lists come out in document order, so one pass through the anchors is enough.
  const anchors = [...document.querySelectorAll<HTMLElement>("a[id]")].filter((anchor) => ANCHOR_ID.test(anchor.id));

  const boxes: Box[] = [];
  let next = 0;
  let anchor: Element | null = null;

  for (const element of document.querySelectorAll<HTMLElement>(".margin")) {
    const origin = element.nextElementSibling;
    if (!origin?.classList.contains("margin-origin")) continue;

    while (next < anchors.length && precedes(anchors[next]!, element)) {
      anchor = anchors[next++]!;
    }

    boxes.push({ element, origin, anchor });
  }

  return boxes;
}

function precedes(node: Element, other: Element): boolean {
  return Boolean(node.compareDocumentPosition(other) & Node.DOCUMENT_POSITION_FOLLOWING);
}

// The pairing has to be read before the first move, while the boxes are still where the
// document put them.
const boxes = collect();

function move() {
  const wide = window.innerWidth > WIDE_FROM;

  for (const { element, origin, anchor } of boxes) {
    const target = wide ? (anchor ?? origin) : origin;
    target.parentNode?.insertBefore(element, target);
  }
}

addEventListener("resize", move);
move();
