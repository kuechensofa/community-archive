function fileSelected(element) {
    const fileContainer = document.querySelector('.record-media');

    const contentType = element.dataset.contentType;
    const url = element.dataset.url;

    let newElement;

    if (!url) {
        newElement = document.createElement("p");
        newElement.textContent = 'No preview available';
    } else if (contentType === "application/pdf") {
        newElement = document.createElement("iframe");
        newElement.src = url;
        newElement.width = "100%";
        newElement.height = "678";
    } else if (contentType.startsWith("image/")) {
        newElement = document.createElement('img');
        newElement.src = url;
        newElement.classList.add("record-image");
    } else if (contentType === "application/wacz") {
        let replayEmbed = document.createElement("replay-web-page");
        replayEmbed.setAttribute("replayBase", "/static/js/");
        replayEmbed.setAttribute("source", url);

        newElement = document.createElement("div");
        newElement.classList.add("replay-embed");
        newElement.append(replayEmbed);
    } else if (contentType.startsWith("video/")) {
        newElement = document.createElement("video");
        newElement.setAttribute('controls', '');
        newElement.setAttribute('width', '100%');
        let sourceElement = document.createElement('source');
        sourceElement.setAttribute('src', url);
        sourceElement.setAttribute('type', 'video/mp4');
        newElement.append(sourceElement);
    } else {
        newElement = document.createElement("p");
        newElement.textContent = 'No preview available';
    }

    if (newElement) {
        fileContainer.replaceChildren(newElement);
    }

    const fileListItems = document.getElementsByClassName("file-list-item");
    for (const listItem of fileListItems) {
        listItem.classList.remove("active");
        listItem.removeAttribute("aria-current");
    }

    element.classList.add("active");
    element.setAttribute("aria-current", "true");
}

$(document).ready(function() {
    $('#inputTag').autocomplete({
        delay: 500,
        minLength: 2,

    })
})