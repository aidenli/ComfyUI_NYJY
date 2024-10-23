import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js"

const link = document.createElement("link")
link.href = "/extensions/ComfyUI_NYJY/css/nyjy.css"
link.rel = 'stylesheet'
link.type = "text/css"
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

		} else if (nodeData.name === "CustomLatentImage") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			const radio_list = {
				"自定义": [0, 0],
				"SDXL - 1:1 square 1024x1024": [
					1024,
					1024,
				],
				"SDXL - 2:3 portrait 832x1216": [
					832,
					1216,
				],
				"SDXL - 3:4 portrait 896x1152": [
					896,
					1152,
				],
				"SDXL - 5:8 portrait 768x1216": [
					768,
					1216,
				],
				"SDXL - 9:16 portrait 768x1344": [
					768,
					1344,
				],
				"SDXL - 9:19 portrait 704x1472": [
					704,
					1472,
				],
				"SDXL - 9:21 portrait 640x1536": [
					640,
					1536,
				],
				"SD1.5 - 1:1 square 512x521": [
					512,
					512,
				],
				"SD1.5 - 2:3 portrait 512x768": [
					512,
					768,
				],
				"SD1.5 - 3:4 portrait 512x682": [
					512,
					682,
				],
				"SD1.5 - 16:9 cinema 910x512": [
					910,
					512,
				],
				"SD1.5 - 1.85:1 cinema 952x512": [
					952,
					512,
				],
				"SD1.5 - 2:1 cinema 1024x512": [
					1024,
					512,
				],
			}
			nodeType.prototype.onNodeCreated = function () {
				const self = this
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
				const wRadio = this.widgets[this.widgets.findIndex((w) => w.name === "radio")]
				const wUpscaleFactor = this.widgets[this.widgets.findIndex((w) => w.name === "upscale_factor")]
				const wWidth = self.widgets[self.widgets.findIndex((w) => w.name === "width")]
				const wHeight = self.widgets[self.widgets.findIndex((w) => w.name === "height")]
				const wSwitch = this.widgets[this.widgets.findIndex((w) => w.name === "switch_width_height")]

				const [width, height] = radio_list[wRadio.value]
				const wUpscaleWidth = ComfyWidgets["INT"](this, "upscale_width", ["INT", { default: width * wUpscaleFactor.value }], app).widget
				const wUpscaleHeight = ComfyWidgets["INT"](this, "upscale_height", ["INT", { default: height * wUpscaleFactor.value }], app).widget

				function refreshSize(width = 0, height = 0) {
					if (width > 0 || height > 0) {
						wWidth.value = width
						wHeight.value = height
					}
					wUpscaleWidth.value = wUpscaleFactor.value * wWidth.value
					wUpscaleHeight.value = wUpscaleFactor.value * wHeight.value
				}

				function handlerSizeChange() {
					wRadio.callback = undefined
					wRadio.value = "自定义"
					refreshSize(0, 0)
					wRadio.callback = handlerRadio
				}

				function handleUpscaleFactor() {
					refreshSize(0, 0)
				}

				function handleSwitch() {
					let nTempWidth = wWidth.value
					wWidth.value = wHeight.value
					wHeight.value = nTempWidth

					let nTempUpWidth = wUpscaleWidth.value
					wUpscaleWidth.value = wUpscaleHeight.value
					wUpscaleHeight.value = nTempUpWidth
				}

				function handlerRadio() {
					let [width, height] = radio_list[this.value]
					if (wSwitch.value){
						[width, height] = [ height,width]
					}
					refreshSize(width, height)
				}

				wRadio.callback = handlerRadio
				wWidth.callback = handlerSizeChange
				wHeight.callback = handlerSizeChange
				wUpscaleFactor.callback = handleUpscaleFactor
				wSwitch.callback = handleSwitch
				this.onResize?.(this.size)
				return r
			}
		}else if (nodeData.name === "FloatSlider") {
			const precisionConfig = {
				"1": {step: 10, round:1, precision: 0},
				"0.1": {step: 1, round:0.1, precision: 1},
				"0.01": {step: 0.1, round:0.01, precision: 2},
				"0.001": {step: 0.01, round:0.001,precision: 3},
			}
			const onNodeCreated = nodeType.prototype.onNodeCreated
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined
				const wNumber = this.widgets[this.widgets.findIndex((w) => w.name === "number")]
				const wMin = this.widgets[this.widgets.findIndex((w) => w.name === "min_value")]
				const wMax = this.widgets[this.widgets.findIndex((w) => w.name === "max_value")]
				const wPrecision = this.widgets[this.widgets.findIndex((w) => w.name === "precision")]

				// step对slider的增量无效，但是对精度有影响，step需要配合precision、round一起设置，并且step是预设值x10
				function updateOptions(){
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
					console.log(wNumber)
				}
				
				setTimeout(updateOptions, 100)

				wMin.callback = function(){
					if (wMin.value >= wMax.value) {
						wMin.value = wMax.value
					}
					updateOptions()
				}
				wMax.callback = function(){
					if (wMin.value >= wMax.value) {
						wMax.value = wMin.value
					}
					updateOptions()
				}

				wPrecision.callback = function(){
					updateOptions()
				}
				return r
			}
		}
	},
	async nodeCreated(node) {
		// console.log(node.comfyClass)
		// setTimeout(() => {
		// 	console.log(node)
		// 	if(node.type === "CustomLatentImage") {
		// 		console.log(arguments[0].type)
		// 		const wRadio = node.widgets[node.widgets.findIndex((w) => w.name === "radio")];
		// 		wRadio.callback = () => {
		// 			console.log("aaaaaaaaaaaaaaaaaaaaa")
		// 		}
		// 	}
		// }, 0)

	}
})
