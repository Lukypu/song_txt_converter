// ==UserScript==
// @name         scraper pisnicky-akordy.cz
// @namespace    Violentmonkey Scripts
// @version      1.0
// @description  Automatically download song text from pisnicky-akordy.cz as .txt
// @match        https://pisnicky-akordy.cz/*
// @grant        none
// @author       hvuzfo
// @description  5. 4. 2026
// ==/UserScript==

(function() {
    'use strict';

    function extractSong() {

        const title = document.querySelector("#songheader h1 a")?.innerText.trim() || "song";
        const author = document.querySelector("#songheader h2 a")?.innerText.trim() || "author";
        let source = "source: pisnicky-akordy.cz"
        const today = new Date().toISOString().slice(0, 10);


        // 1 Get song text from <pre> or fallback selectors
        let text = document.querySelector("#songtext")?.textContent || "";

        //remove first line if it's empty
        text = text.replace(/^[ \t]*\r?\n/, "");
        // Remove first two tabs on the very first line only
        text = text.replace(/^(\t){1,2}/, "");

        text = text.replace(/\n\s+\n/g, "\n\n"); // clean empty lines
        text = text.replace(/\n\n\n/g, "\n\n"); // clean empty double lines

        text = `${title}\n${author}\n\n${source}\ndate: ${today}\n\n` + text;

        console.log(text);

        return text;
    }

    function download(text) {

        const title = document.querySelector("#songheader h1 a")?.innerText.trim() || "song";
        const author = document.querySelector("#songheader h2 a")?.innerText.trim() || "author";

        // filename
        // const filename = `${author}-${title}.txt`;
        // Prepare filename: lowercase, underscores
        const filename = `${author.toLowerCase().replace(/\s+/g, "_")}-${title.toLowerCase().replace(/\s+/g, "_")}-piasg.txt`;


        // Create blob and trigger download
        const blob = new Blob([text], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
    }



    function handler(e) {
        // Ctrl + Alt + D
        if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'd') {
            console.log("Shortcut triggered");

            const text = extractSong();
            if (text) {
                download(text);
            } else {
                alert("Failed to extract song.");
            }
        }
    }

    window.addEventListener("keydown", handler);

})();
