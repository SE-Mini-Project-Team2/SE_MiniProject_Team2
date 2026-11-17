/* Ask the customer to confirm before a book is added to the cart.
   Without JavaScript (or <dialog> support) the form submits normally. */
(function () {
    var dialog = document.getElementById("confirm-add");
    if (!dialog || typeof dialog.showModal !== "function") { return; }

    var bookLine = document.getElementById("confirm-add-book");
    var pending = null;

    document.addEventListener("submit", function (event) {
        var form = event.target;
        if (!form.hasAttribute("data-confirm-add")) { return; }
        event.preventDefault();
        pending = form;
        bookLine.textContent = form.getAttribute("data-book-title") || "";
        dialog.showModal();
    });

    document.getElementById("confirm-add-yes").addEventListener("click", function () {
        var form = pending;
        pending = null;
        dialog.close();
        if (form) { form.submit(); }
    });

    function discard() { pending = null; dialog.close(); }
    document.getElementById("confirm-add-no").addEventListener("click", discard);
    dialog.addEventListener("cancel", function () { pending = null; });
    dialog.addEventListener("click", function (event) {
        if (event.target === dialog) { discard(); }
    });
})();
