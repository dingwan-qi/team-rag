const state = {
    token: localStorage.getItem("teamrag_token"),
    user: JSON.parse(localStorage.getItem("teamrag_user") || "null"),
    documents: [],
    graph: { nodes: [], edges: [] },
};

const messageList = document.getElementById("messageList");
const questionInput = document.getElementById("questionInput");
const topK = document.getElementById("topK");
const topKLabel = document.getElementById("topKLabel");
const ragMode = document.getElementById("ragMode");
const toast = document.getElementById("toast");

if (!state.token || !state.user) {
    window.location.href = "start.html";
}

document.getElementById("currentUser").textContent = state.user?.username || "未登录";

document.querySelectorAll(".nav-btn").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
});

topK.addEventListener("input", () => {
    topKLabel.textContent = topK.value;
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
    try {
        await api("/api/auth/logout", { method: "POST" });
    } finally {
        localStorage.removeItem("teamrag_token");
        localStorage.removeItem("teamrag_user");
        window.location.href = "start.html";
    }
});

document.getElementById("chatForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = questionInput.value.trim();
    if (!query) return;
    questionInput.value = "";
    appendMessage("user", query);
    await askQuestion(query);
});

document.getElementById("clearMemoryBtn").addEventListener("click", async () => {
    await api("/api/memory", { method: "DELETE" });
    messageList.innerHTML = "";
    renderEmptyChat();
    showToast("聊天记忆已清空", "success");
});

document.getElementById("uploadForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const file = document.getElementById("fileInput").files[0];
    if (!file) {
        showToast("请选择要上传的课程资料", "error");
        return;
    }
    const formData = new FormData();
    formData.append("file", file);
    await api("/api/documents/upload", {
        method: "POST",
        body: formData,
        skipJsonHeader: true,
    });
    showToast("上传并索引完成", "success");
    document.getElementById("fileInput").value = "";
    await loadDocuments();
});

document.getElementById("refreshDocsBtn").addEventListener("click", loadDocuments);

document.getElementById("buildIndexBtn").addEventListener("click", async () => {
    const result = await api("/api/knowledge-base/index", { method: "POST" });
    showToast(result.message || "索引已重建", "success");
    await loadDocuments();
});

document.getElementById("buildGraphBtn").addEventListener("click", async () => {
    const result = await api("/api/knowledge-base/graph", { method: "POST" });
    showToast(result.message || "图谱已构建", "success");
    await loadGraph();
});

document.getElementById("evaluationForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const questions = document
        .getElementById("evaluationQuestions")
        .value.split("\n")
        .map((line) => line.trim())
        .filter(Boolean);
    if (!questions.length) {
        showToast("请至少输入一个评估问题", "error");
        return;
    }
    const result = await api("/api/evaluate", {
        method: "POST",
        body: JSON.stringify({ questions, top_k: Number(topK.value) }),
    });
    renderEvaluation(result.rows || []);
});

async function boot() {
    try {
        await api("/api/auth/me");
        await Promise.all([loadMemory(), loadDocuments(), loadGraph()]);
    } catch (error) {
        localStorage.removeItem("teamrag_token");
        localStorage.removeItem("teamrag_user");
        window.location.href = "start.html";
    }
}

function switchView(view) {
    document.querySelectorAll(".nav-btn").forEach((button) => {
        button.classList.toggle("active", button.dataset.view === view);
    });
    document.querySelectorAll(".view").forEach((section) => {
        section.classList.toggle("active", section.id === `view-${view}`);
    });
}

async function askQuestion(query) {
    const pending = appendMessage("assistant", "正在检索课程资料并生成答案...");
    try {
        const result = await api("/api/chat", {
            method: "POST",
            body: JSON.stringify({
                query,
                rag_mode: ragMode.value,
                top_k: Number(topK.value),
            }),
        });
        pending.remove();
        appendMessage("assistant", result.answer, result);
    } catch (error) {
        pending.remove();
        appendMessage("assistant", `请求失败：${error.message}`);
        showToast(error.message, "error");
    }
}

async function loadMemory() {
    const result = await api("/api/memory");
    messageList.innerHTML = "";
    const messages = result.messages || [];
    if (!messages.length) {
        renderEmptyChat();
        return;
    }
    messages.forEach((message) => appendMessage(message.role, message.content));
}

function renderEmptyChat() {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "还没有聊天记录。上传课程资料后，可以在这里开始提问。";
    messageList.appendChild(empty);
}

function appendMessage(role, content, response = null) {
    const empty = messageList.querySelector(".empty-state");

    if (empty) {
        empty.remove();
    }

    const node = document.createElement("div");
    node.className = `message ${role}`;

    const contentNode = document.createElement("div");
    contentNode.className = "message-content";
    contentNode.textContent = content;
    node.appendChild(contentNode);

    if (response) {
        const sources = Array.isArray(response.sources)
            ? response.sources
            : [];

        const meta = document.createElement("div");
        meta.className = "message-meta";
        meta.textContent =
            `模式：${response.rag_mode || "未知"} · ` +
            `耗时：${response.latency ?? "-"}s · ` +
            `引用：${sources.length}`;

        node.appendChild(meta);

        if (sources.length > 0) {
            const details = document.createElement("details");
            details.className = "source-details";

            const summary = document.createElement("summary");
            summary.textContent = `查看引用来源（${sources.length}）`;
            details.appendChild(summary);

            sources.forEach((source, index) => {
                const sourceItem = document.createElement("div");
                sourceItem.className = "source-item";

                const filename =
                    source.filename ||
                    source.source ||
                    source.document_name ||
                    "未知文件";

                const pageNumber =
                    source.page_number ??
                    source.page ??
                    source.page_index;

                const page =
                    pageNumber !== undefined &&
                    pageNumber !== null &&
                    pageNumber !== ""
                        ? ` · 第 ${pageNumber} 页`
                        : "";

                const numericScore = Number(source.score);

                const score = Number.isFinite(numericScore)
                    ? ` · 相关度 ${numericScore.toFixed(3)}`
                    : "";

                sourceItem.textContent =
                    `${index + 1}. ${filename}${page}${score}`;

                details.appendChild(sourceItem);
            });

            node.appendChild(details);
        }

        const trace = Array.isArray(response.trace)
            ? response.trace
            : [];

        if (trace.length > 0) {
            const traceDetails = document.createElement("details");
            traceDetails.className = "source-details";

            const traceSummary = document.createElement("summary");
            traceSummary.textContent = "查看执行轨迹";
            traceDetails.appendChild(traceSummary);

            trace.forEach((step, index) => {
                const traceItem = document.createElement("div");
                traceItem.className = "source-item";

                const name = step.name || `步骤${index + 1}`;
                const detail = step.detail || "";
                const tool = step.tool
                    ? ` · 工具：${step.tool}`
                    : "";

                traceItem.textContent =
                    `${index + 1}. ${name}：${detail}${tool}`;

                traceDetails.appendChild(traceItem);
            });

            node.appendChild(traceDetails);
        }
    }

    messageList.appendChild(node);
    messageList.scrollTop = messageList.scrollHeight;

    return node;
}

async function loadDocuments() {
    state.documents = await api("/api/documents");
    const tbody = document.getElementById("documentTable");
    tbody.innerHTML = "";
    if (!state.documents.length) {
        const row = document.createElement("tr");
        row.innerHTML = '<td colspan="4">暂无文档，请先上传课程资料。</td>';
        tbody.appendChild(row);
        return;
    }
    state.documents.forEach((doc) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${escapeHtml(doc.filename)}</td>
            <td>${escapeHtml(doc.file_type)}</td>
            <td>${doc.chunk_count}</td>
            <td>${escapeHtml(doc.status)}</td>
        `;
        tbody.appendChild(row);
    });
}

async function loadGraph() {
    state.graph = await api("/api/graph");
    const nodes = state.graph.nodes || [];
    const edges = state.graph.edges || [];
    document.getElementById("nodeCount").textContent = nodes.length;
    document.getElementById("edgeCount").textContent = edges.length;

    const nodeList = document.getElementById("nodeList");
    nodeList.innerHTML = "";
    nodes.slice(0, 80).forEach((node) => {
        const item = document.createElement("span");
        item.className = "pill";
        item.textContent = node.label || node.id || String(node);
        nodeList.appendChild(item);
    });
    if (!nodes.length) nodeList.textContent = "暂无实体，请先构建图谱。";

    const edgeList = document.getElementById("edgeList");
    edgeList.innerHTML = "";
    edges.slice(0, 80).forEach((edge) => {
    const item = document.createElement("div");
    item.className = "edge-item";

    const source = edge.source || edge.from || "未知节点";
    const target = edge.target || edge.to || "未知节点";
    const relation = edge.relation || edge.label || "";

    item.textContent = `${source} → ${target}${
        relation ? `（${relation}）` : ""
    }`;

    edgeList.appendChild(item);
});
    if (!edges.length) edgeList.textContent = "暂无关系，请先构建图谱。";
}

function renderEvaluation(rows) {
    const container = document.getElementById("evaluationResults");
    container.innerHTML = "";
    if (!rows.length) {
        container.textContent = "暂无评估结果。";
        return;
    }
    rows.forEach((row) => {
        const item = document.createElement("div");
        item.className = "evaluation-row";
        item.innerHTML = `
            <h4>${escapeHtml(row.question)}</h4>
            <p>${escapeHtml(row.answer)}</p>
            <div class="message-meta">模式：${row.rag_mode} · 检索：${row.retrieval_count} · 引用：${row.citation_count} · 耗时：${row.latency}s</div>
        `;
        container.appendChild(item);
    });
}

async function api(path, options = {}) {
    const headers = options.skipJsonHeader ? {} : { "Content-Type": "application/json" };
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    const response = await fetch(path, {
        method: options.method || "GET",
        headers,
        body: options.body,
    });
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();
    if (!response.ok) {
        throw new Error(data.detail || data || "请求失败");
    }
    return data;
}

function showToast(message, type = "") {
    toast.textContent = message;
    toast.className = `toast visible ${type}`.trim();
    setTimeout(() => {
        toast.className = "toast";
    }, 2600);
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

boot();
