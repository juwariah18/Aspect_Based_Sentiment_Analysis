const input = document.getElementById("reviewInput");
const status = document.getElementById("analysisStatus");

const positiveWords = new Map(Object.entries({
    amazing: 2.5, awesome: 2.5, best: 2.5, beautiful: 1.7, excellent: 2.7,
    fantastic: 2.7, good: 1.5, great: 2, happy: 1.8, love: 2.5, loved: 2.5,
    perfect: 2.7, pleased: 1.8, recommend: 1.8, satisfied: 1.8, nice: 1.4,
    pretty: 1.5,
    comfortable: 1.5, smooth: 1.3, soft: 1.2, quick: 1.2, easy: 0.8,
    reliable: 1.7, sturdy: 1.5, useful: 1.2, works: 0.35, working: 0.35,
    luckily: 0.65, perfectly: 1.5
}));
const negativeWords = new Map(Object.entries({
    awful: -2.7, bad: -1.8, broken: -2.7, damaged: -2.4, disappointing: -2.2,
    disappointed: -2.2, defective: -2.7, hate: -2.5, horrible: -2.7,
    late: -1.4, missing: -2, poor: -2, problem: -1.5, problems: -1.5,
    return: -1.1, returned: -1.1, stopped: -2.1, terrible: -2.7, tight: -1.6,
    uncomfortable: -1.8, useless: -2.5, waste: -2.5, worst: -2.7, wrong: -1.8,
    slow: -1.5, ugly: -1.6, difficult: -1.2, expensive: -0.8, weird: -1.5,
    leak: -2.5, leaks: -2.5, leaking: -2.5, leaked: -2.5, leakage: -2.5,
    draining: -1.8, overheats: -2, overheating: -2, crashed: -2.2, crashing: -2.2,
    freezing: -1.8, disconnecting: -1.8, thin: -0.4, faded: -1.7
}));
const negations = new Set(["not", "no", "never", "without", "hardly"]);
const intensifiers = new Set(["very", "really", "extremely", "absolutely", "so"]);
const contrastWords = new Set(["but", "however", "although", "though", "yet"]);
const sentimentEmojis = { positive: "😊", negative: "😞", neutral: "😐", mixed: "😐" };
const specialPhrases = [
    [/\b(?:exceeded|exceeds|exceeding) (?:my |our )?expectations?\b|\bbetter than (?:i |we )?expected\b|\bmore than (?:i |we )?expected\b|\babove (?:my |our )?expectations?\b|\btoo good than expected\b/gi, 2.5],
    [/\bnot as expected\b|\bbelow (?:my |our )?expectations?\b|\bshort of (?:my |our )?expectations?\b/gi, -2],
    [/\btoo (?:thin|small|big|short|long|tight|loose|heavy|light|slow|noisy|loud|hard|soft)\b/gi, -2],
    [/\bnot like (?:the )?(?:one )?(?:shown|pictured|advertised|online|on the website)\b|\bnot (?:as|what) shown\b|\bnot the same as (?:the )?(?:picture|pictures|website|advertised)\b/gi, -2.5],
    [/\b(?:actual )?colou?r (?:is )?lighter than (?:the )?(?:picture|pictures|shown|expected)\b/gi, -2.4],
    [/\b(?:looks|is|was) (?:really |very |so )?(?:pretty|beautiful|gorgeous|lovely)\b/gi, 2],
    [/\b(?:fits?|fit) perfectly\b|\bmatches? (?:the )?(?:photos|pictures|description)\b|\bexactly as (?:shown|described|expected)\b/gi, 1.8],
    [/\b(?:does not|doesn't|did not|didn't|is not|isn't|was not|wasn't) work(?:ing)?\b|\bnot working\b|\bstopped working\b/gi, -2.8],
    [/\bworking slow(?:ly)?\b|\bslow(?:ly)? (?:computer|laptop|phone|device|performance)\b/gi, -2.5],
    [/\bbattery (?:is )?(?:draining|drains|dies) (?:too )?(?:fast|quickly)\b|\b(?:fast|quick) battery drain(?:ing)?\b/gi, -3],
    [/\b(?:lipstick|makeup|product|item|container|bottle)s? (?:is |are |was |were )?(?:leaking|leaked)\b|\b(?:leaking|leaked|leakage) (?:from|through) (?:the )?(?:packaging|package|box|container)\b/gi, -3],
    [/\b(?:next time )?please (?:pack|wrap|seal|send|handle) (?:it|them|this|these|the .+?) properly\b/gi, -2.5],
    [/\bnext time please\b.{0,50}\bproperly\b/gi, -2.5],
    [/\bnot worth (?:it|the (?:price|money))\b|\bwaste of (?:money|time)\b/gi, -2.5],
    [/\b(?:on time|as described|as shown|as expected|met (?:my |our )?expectations?)\b/gi, 0]
];

function splitIntoSentences(text) {
    const clauses = (text.match(/[^.!?\n]+[.!?]?/g) || [])
        .flatMap(sentence => sentence
            .split(/(?<=,)\s*|(?=\b(?:but|also|however|although|though|yet)\b)/i))
        .map(sentence => sentence.trim())
        .filter(Boolean);
    return clauses.reduce((sentences, clause) => {
        if (/^(?:but|also|however|although|though|yet)[.!?]*$/i.test(clause) && sentences.length) {
            sentences[sentences.length - 1] += ` ${clause}`;
        } else {
            sentences.push(clause);
        }
        return sentences;
    }, []);
}

function normalize(text) {
    return text.toLowerCase()
        .replace(/n't\b/g, " not")
        .replace(/'re\b/g, " are")
        .replace(/'m\b/g, " am")
        .replace(/'ve\b/g, " have")
        .replace(/'ll\b/g, " will")
        .replace(/'d\b/g, " would")
        .replace(/'s\b/g, " is")
        .replace(/[^a-z0-9\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function scoreSentence(sentence) {
    const clean = normalize(sentence);
    let score = 0;

    for (const [pattern, value] of specialPhrases) {
        if (pattern.test(clean)) score += value;
        pattern.lastIndex = 0;
    }

    const words = clean.split(" ");
    words.forEach((word, index) => {
        let value = positiveWords.get(word) || negativeWords.get(word) || 0;
        if (!value) return;

        if (index > 0 && intensifiers.has(words[index - 1])) value *= 1.4;
        const negated = words.slice(Math.max(0, index - 3), index).some(token => negations.has(token));
        if (negated) value = value < 0 ? Math.abs(value) * 0.5 : -value;

        const contrastIndex = words.findIndex((token, i) => i < index && contrastWords.has(token));
        score += value * (contrastIndex >= 0 ? 1.35 : 0.7);
    });

    if (score >= 0.7) return { sentiment: "positive", score };
    if (score <= -0.7) return { sentiment: "negative", score };
    return { sentiment: "neutral", score };
}

function renderResults(sentences, predictions) {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    const list = document.getElementById("aspectList");
    const highlights = document.getElementById("highlightedText");
    list.replaceChildren();
    highlights.replaceChildren();

    sentences.forEach((sentence, index) => {
        const { sentiment } = predictions[index];
        counts[sentiment]++;

        const item = document.createElement("div");
        item.className = `aspect-item ${sentiment}`;
        const info = document.createElement("div");
        info.className = "aspect-info";
        const name = document.createElement("div");
        name.className = "aspect-name";
        name.textContent = `Sentence ${index + 1}`;
        const context = document.createElement("div");
        context.className = "aspect-context";
        context.textContent = sentence;
        const badge = document.createElement("span");
        badge.className = `sentiment-badge ${sentiment}`;
        badge.textContent = `${sentimentEmojis[sentiment]} ${sentiment}`;
        info.append(name, context);
        item.append(info, badge);
        list.append(item);

        if (index) highlights.append(document.createTextNode(" "));
        const highlight = document.createElement("span");
        highlight.className = sentiment === "positive" ? "hl-pos" :
            sentiment === "negative" ? "hl-neg" : "hl-neu";
        highlight.textContent = sentence;
        highlights.append(highlight);
    });

    const highestCount = Math.max(counts.positive, counts.negative, counts.neutral);
    const leadingSentiments = Object.keys(counts).filter(sentiment =>
        counts[sentiment] === highestCount);
    const overall = leadingSentiments.length === 1 ? leadingSentiments[0] : "mixed";

    const overallElement = document.getElementById("overallSentiment");
    overallElement.textContent = `${sentimentEmojis[overall]} ${overall[0].toUpperCase() + overall.slice(1)}`;
    overallElement.className = `stat-value ${overall === "positive" ? "pos" :
        overall === "negative" ? "neg" : "neu"}`;
    document.getElementById("posCount").textContent = counts.positive;
    document.getElementById("negCount").textContent = counts.negative;
    document.getElementById("neuCount").textContent = counts.neutral;
    document.getElementById("results").classList.add("show");
}

function analyzeReview() {
    const text = input.value.trim();
    if (!text) {
        status.textContent = "Please enter a customer review first.";
        status.classList.add("error");
        return;
    }

    status.classList.remove("error");
    const sentences = splitIntoSentences(text);
    renderResults(sentences, sentences.map(scoreSentence));
    status.textContent = "Analysis complete.";
}

function loadSample() {
    input.value = "The delivery was quick, the product was packed properly and everything was exactly as shown in the picture. The toy was working when I opened it, but it stopped working the next day. Waste of money. I received the product two days late and the box was damaged. Luckily the item was working.";
    analyzeReview();
}

function clearAll() {
    input.value = "";
    document.getElementById("results").classList.remove("show");
    status.classList.remove("error");
    status.textContent = "Ready to analyze.";
}

function downloadReport() {
    const overall = document.getElementById("overallSentiment").textContent;
    const counts = [
        `😊 Positive: ${document.getElementById("posCount").textContent}`,
        `😞 Negative: ${document.getElementById("negCount").textContent}`,
        `😐 Neutral: ${document.getElementById("neuCount").textContent}`
    ];
    const sentences = [...document.querySelectorAll("#aspectList .aspect-item")].map(item => {
        const label = item.querySelector(".aspect-name").textContent;
        const reviewText = item.querySelector(".aspect-context").textContent;
        const sentiment = item.querySelector(".sentiment-badge").textContent;
        return `${label} [${sentiment}]: ${reviewText}`;
    });
    const report = [
        "Customer Review Sentiment Report",
        `Generated: ${new Date().toLocaleString()}`,
        "",
        "Review:",
        input.value.trim(),
        "",
        `Overall sentiment: ${overall}`,
        ...counts,
        "",
        "Sentence analysis:",
        ...sentences
    ].join("\n");

    const url = URL.createObjectURL(new Blob([report], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "sentiment-report.txt";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

document.getElementById("analyzeButton").addEventListener("click", analyzeReview);
document.getElementById("sampleButton").addEventListener("click", loadSample);
document.getElementById("clearButton").addEventListener("click", clearAll);
document.getElementById("downloadButton").addEventListener("click", downloadReport);
input.addEventListener("keydown", event => {
    if (event.ctrlKey && event.key === "Enter") {
        event.preventDefault();
        analyzeReview();
    }
});
