// ==UserScript==
// @name        Scraper ultimate-guitar.com
// @namespace   Violentmonkey Scripts
// @icon        data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACqklEQVRYR81XP2hTQRi/S9rktSg1Wzo06OCm0LpaWqcODeogKBURpUuhgjhV2o4iZFIhgS7VQVC6iAbsapG62kKc7CLtYDZTFJuXP31+v7OHL6/v3Z1nYvrBg7y7vO/7/b6/d5yRpNPpk67rPqOfw/ScwFoHpUK615LJ5L1yufyFHxjf+A+Gg5wqBGKEp1Kp17RzuYOMVarXAOBbF9hLUBUA8LrEXpi1BnDm9D4bOOax3R+cfdqKtXDA+sy1htiff5JQ8lMCmJpssO2vnH3YiAslUvHM1TobOP7HcfhPbjnBVt/HhWG5f+O+I9ZUogVQWHQFiKWVBCmvs8zgvnHEhq/0i2+tAYDx5qs9wRyy/jHOXq72CKXwQHasyeClMCl9jrHxW31asNocgAdgJLfcK9wclLnpGpubrh9aB9DZB8l/BzA6QiyzDaUyCdJvzST+xlWQGfSUsQTIYqHawvbURL+oEJ1oQ6BTIPeHCKRfdpAnB+VYojKNqoa2AfAbD5YrcgE5ESZtBRDVJ6wB6GIvGaErovlcp2QNE2sA5ym5ZBcMU4x9lODouaYyVawBoP6jYgeL8NDUZJ2eprJDWgMAOzQgE4E3MAeyY4fDYA2gmN9jl+7o26kEmF9wQ/PAGsDDuzW2XY7RIAovIb9nMmnMjZ8tzro46whAL972ROaSsgzR4Z7nXDZ+s4+ARHc1GEcn9E/Kts0CKD5LZTb/OBGakIh9YbHWYnz3OxeTUDeKjWYBMr2Y/80OCktbcXECGqJ3AMMTFJyCllbMkteoE/pBqCoCzHNPe42NG3lAGlTVPAyv07FtgZibuN1PwsgDQdbyQApQmHQ7lKAAYSNWAGwMRX1zJC4m7wjdhXay+gtdb7p/OQVa3JCr1eojzjk80fHrued5m47j3Mb1/BcKVUXJ+SA2OwAAAABJRU5ErkJggg==
// @grant       none
// @version     1.0
// @author      hvuzfo
// @description 5. 4. 2026
// @match       https://tabs.ultimate-guitar.com/*
// ==/UserScript==

(function() {
    'use strict';

    function extractSong() {

        let title = "song";
        let author = "artist";
        let source = "source: ultimate-guitar.com"
        const today = new Date().toISOString().slice(0, 10);

//         const raw = document.title;
//
//         const match = raw.match(/^(.*?)\s+CHORDS.*?by\s+(.*?)\s+@/i);
//         if (match) {
//             title = match[1].trim();
//             author = match[2].trim();
//         }

//         title = title.toLowerCase();
//         title = title.charAt(0).toUpperCase() + title.slice(1);

        const meta = document.querySelector('meta[name="keywords"]')?.getAttribute("content");
        const match = meta.match(/^(.*?)\s*-\s*(.*?)\s*\(.*?\)/i);
        if (match) {
            author = match[1].trim();
            title = match[2].trim();
        }

        const data = window.UGAPP?.store?.page;
        if (!data) {
            console.log("UG data not found");
            return null;
        }

        let content =
            data?.data?.tab_view?.wiki_tab?.content ||
            data?.data?.tab_view?.tab?.content;

        if (!content) {
            console.log("No content found");
            return null;
        }

        // Decode HTML entities
        const textarea = document.createElement("textarea");
        textarea.innerHTML = content;
        let text = textarea.value;

        // Strip HTML tags
        text = text.replace(/<[^>]+>/g, "");

        // strip ultimate-guitar tags (everything in square brackets)
        // text = text.replace(/\[[^\]]*\]/g, ""); // simple version -- removes everything
        text = text.replace(/\[(?!\s*(verse|chorus|bridge|intro|instrumental|break)\s*\d*\b)[^\]]*\]/gi, "");
        text = text.replace(/\n\s+\n/g, "\n\n"); // clean empty lines
        text = text.replace(/\n\n\n/g, "\n\n"); // clean empty double lines

        text = `${title}\n${author}\n\n${source}\ndate: ${today}\n\n` + text;

        return text.trim();
    }

    function download(text) {

        const raw = document.title;

        let title = "song";
        let author = "artist";

        const match = raw.match(/^(.*?)\s+CHORDS.*?by\s+(.*?)\s+@/i);
        if (match) {
            title = match[1].trim();
            author = match[2].trim();
        }

        // const filename = `${author}-${title}.txt`;
        // Prepare filename: lowercase, underscores
        const filename = `${author.toLowerCase().replace(/\s+/g, "_")}-${title.toLowerCase().replace(/\s+/g, "_")}-ultsg.txt`;

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
