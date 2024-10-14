import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js"

const link = document.createElement("link")
link.href="/extensions/ComfyUI_NYJY/css/nyjy.css"
link.rel='stylesheet'
link.type="text/css"
document.head.appendChild(link)

app.registerExtension({
	name: "NYJY.jsnodes",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.python_module !== "custom_nodes.ComfyUI_NYJY") {
			return
		}

		if (nodeData.name === "Translate") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "preview_text");
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemove?.();
						}
						this.widgets.length = pos;
					}
				}

				const w = ComfyWidgets["STRING"](this, "preview_text", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 1;
				w.value = message.text;

				this.onResize?.(this.size);
			}
		} else if (nodeData.name === "CivitaiPrompt") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "positive_text");
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemove?.();
						}
						this.widgets.length = pos;
					}
				}
				
				["positive_text", "negative_text"].forEach(str => {
					console.log(message[str])
					const w = ComfyWidgets["STRING"](this, str, ["STRING", { multiline: true }], app).widget;
					w.inputEl.readOnly = true;
					w.inputEl.style.opacity = 1;
					w.value = message[str];
				})
				
				this.onResize?.(this.size);
			}
		} else if (nodeData.name === "JoyCaptionAlpha2Online") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "text");
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemove?.();
						}
						this.widgets.length = pos;
					}
				}

				const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 1;
				w.value = message["text"];

				this.onResize?.(this.size);
			}
		}
	},
})
