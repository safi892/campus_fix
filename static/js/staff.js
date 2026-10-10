/**
 * CampusFix AI — Staff dashboard interactions.
 *  - Status dropdown  -> POST /api/status/update
 *  - Accept Merge     -> POST /api/cluster/merge
 *  - Keep Separate    -> POST /api/cluster/dismiss
 * API URLs come from data-* attributes on #staffBoard (rendered by Flask url_for).
 * All user text is written with textContent, never innerHTML.
 */
(() => {
    "use strict";

    const board = document.getElementById("staffBoard");
    if (!board) return;

    const urls = {
        status: board.dataset.statusUrl,
        merge: board.dataset.mergeUrl,
        dismiss: board.dataset.dismissUrl,
    };
    const csrfToken = board.dataset.csrfToken;
    const RELOAD_AFTER_MERGE_MS = 1200;
    const CARD_EXIT_MS = 350;

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------
    async function postJson(url, payload) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken,
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.success) {
            throw new Error(data.error || "Request failed. Please try again.");
        }
        return data;
    }

    function notify(message, tone = "success") {
        const toastEl = document.getElementById("staffToast");
        toastEl.classList.remove("text-bg-success", "text-bg-danger");
        toastEl.classList.add(tone === "success" ? "text-bg-success" : "text-bg-danger");
        document.getElementById("staffToastBody").textContent = message;
        bootstrap.Toast.getOrCreateInstance(toastEl).show();
    }

    function removeSuggestionCard(card) {
        card.classList.add("is-leaving");
        setTimeout(() => {
            card.remove();
            const remaining = document.querySelectorAll(".js-suggestion").length;
            document.getElementById("suggestionCount").textContent = `${remaining} pending`;
            document.getElementById("suggestionEmpty").classList.toggle("d-none", remaining > 0);
        }, CARD_EXIT_MS);
    }

    function setBusy(card, busy) {
        card.querySelectorAll("button").forEach((button) => { button.disabled = busy; });
    }

    // ------------------------------------------------------------------
    // Status updates
    // ------------------------------------------------------------------
    document.querySelectorAll(".js-status-select").forEach((select) => {
        select.dataset.previous = select.value;

        select.addEventListener("change", async () => {
            const id = Number(select.dataset.jobId);
            select.disabled = true;
            try {
                await postJson(urls.status, { id, status: select.value });
                select.dataset.previous = select.value;
                notify(`Job #${id} marked "${select.value}". Linked student reports updated too.`);
            } catch (error) {
                select.value = select.dataset.previous;   // roll back the UI
                notify(error.message, "danger");
            } finally {
                select.disabled = false;
            }
        });
    });

    // ------------------------------------------------------------------
    // AI review deck
    // ------------------------------------------------------------------
    document.querySelectorAll(".js-suggestion").forEach((card) => {
        const parentId = Number(card.dataset.parentId);
        const childId = Number(card.dataset.childId);

        card.querySelector(".js-accept").addEventListener("click", async () => {
            setBusy(card, true);
            try {
                const data = await postJson(urls.merge, { parent_id: parentId, child_id: childId });

                // Instant feedback: bump the parent's counter, drop the child from the queue.
                document
                    .querySelectorAll(`[data-job-id="${parentId}"] .js-volume-count`)
                    .forEach((el) => { el.textContent = data.new_count; el.classList.add("count-pop"); });
                document.querySelector(`.job-card[data-job-id="${childId}"]`)?.remove();

                removeSuggestionCard(card);
                notify(`${data.message} Cluster now has ${data.new_count} reports.`);

                // Re-render from the server so queue order and cluster lists stay the source of truth.
                setTimeout(() => window.location.reload(), RELOAD_AFTER_MERGE_MS);
            } catch (error) {
                setBusy(card, false);
                notify(error.message, "danger");
            }
        });

        card.querySelector(".js-dismiss").addEventListener("click", async () => {
            setBusy(card, true);
            try {
                await postJson(urls.dismiss, { complaint_id: childId });
                removeSuggestionCard(card);
                notify("Kept as a separate report. It won't be suggested again.");
            } catch (error) {
                setBusy(card, false);
                notify(error.message, "danger");
            }
        });
    });
})();
