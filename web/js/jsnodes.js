import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js"

app.registerExtension({
	name: "NYJY.jsnodes",
		async beforeRegisterNodeDef(nodeType, nodeData, app) {
		
		if(!nodeData?.category?.startsWith("NYJY")) {
			return;
		}
		if (nodeData.name === "Translate") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "preview_text");
					let w;
					if (pos === -1) {
						w = this.widgets[pos]
					} else {
						w = ComfyWidgets["STRING"](this, "preview_text", ["STRING", { multiline: true }], app).widget;
						w.inputEl.readOnly = true;
						w.inputEl.style.opacity = 1;
					}
					w.value = message["text"][0];
				}

				this.onResize?.(this.size);
			}
		}  else if (nodeData.name === "FloatSlider-NYJY") {
			const precisionConfig = {
				"1": { step: 10, round: 1, precision: 0 },
				"0.1": { step: 1, round: 0.1, precision: 1 },
				"0.01": { step: 0.1, round: 0.01, precision: 2 },
				"0.001": { step: 0.01, round: 0.001, precision: 3 },
			}
			const onNodeCreated = nodeType.prototype.onNodeCreated
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined
				const wNumber = this.widgets[this.widgets.findIndex((w) => w.name === "number")]
				const wMin = this.widgets[this.widgets.findIndex((w) => w.name === "min_value")]
				const wMax = this.widgets[this.widgets.findIndex((w) => w.name === "max_value")]
				const wPrecision = this.widgets[this.widgets.findIndex((w) => w.name === "precision")]

				// step对slider的增量无效，但是对精度有影响，step需要配合precision、round一起设置，并且step是预设值x10
				function updateOptions() {
					const confItem = precisionConfig[wPrecision.value]
					wNumber.options.min = wMin.value
					wNumber.options.max = wMax.value
					wNumber.options.step = confItem.step
					wNumber.options.precision = confItem.precision
					wNumber.options.round = confItem.round
					wMin.options.step = confItem.step
					wMin.options.precision = confItem.precision
					wMax.options.step = confItem.step
					wMax.options.precision = confItem.precision
				}

				setTimeout(updateOptions, 100)

				wMin.callback = function () {
					if (wMin.value >= wMax.value) {
						wMin.value = wMax.value
					}
					updateOptions()
				}
				wMax.callback = function () {
					if (wMin.value >= wMax.value) {
						wMax.value = wMin.value
					}
					updateOptions()
				}

				wPrecision.callback = function () {
					updateOptions()
				}
				return r
			}
		}else if (["JsonGetValueByKeys", "JsonDumps", "JsonLoads", "GetItemFromList"].includes(nodeData.name)) {
			console.log(nodeData.name)
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "preview_text");
					let w;
					if (pos === -1) {
						w = ComfyWidgets["STRING"](this, "preview_text", ["STRING", { multiline: true }], app).widget;
					} else {
						w = this.widgets[pos];
					}
					w.inputEl.readOnly = true;
					w.inputEl.style.opacity = 1;
					w.value = message["text"][0];
				}
				this.onResize?.(this.size);
			}
		}
	}
})
