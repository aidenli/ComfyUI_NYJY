import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js"

function addMenuHandler(nodeType, cb) {
	const getOpts = nodeType.prototype.getExtraMenuOptions;
	nodeType.prototype.getExtraMenuOptions = function () {
		const r = getOpts.apply(this, arguments);
		cb.apply(this, arguments);
		return r;
	};
}


app.registerExtension({
	name: "NYJY.jsnodes",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {

		if (!nodeData?.category?.startsWith("NYJY")) {
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
		} else if (["CustomLatentImage-NYJY", "QwenLatentImage"].includes(nodeData.name)) {
			addMenuHandler(nodeType, function (_, options) {
				options.push({
					content: "Swap width/height",
					callback: () => {
						const wRatio = this.widgets[this.widgets.findIndex((w) => w.name === "ratio")]
						console.log(wRatio)
						const wWidth = this.widgets[this.widgets.findIndex((w) => w.name === "width_override")]
						const wHeight = this.widgets[this.widgets.findIndex((w) => w.name === "height_override")]
						const oriH = wHeight.value, oriW = wWidth.value
						wWidth.value = oriH
						wHeight.value = oriW

						if (oriH <= 0 && oriW <= 0) {
							// swap ratio
							const reg = /^(\d+):(\d+)\s+/
							const match = wRatio.value.match(reg)
							if (match) {
								const swapItem = wRatio.options.values.find((item) => item.indexOf(`${match[2]}:${match[1]}`) > -1)
								if (swapItem) {
									wRatio.value = swapItem
								}
							}
						}
					},
				});
			});
		} else if (nodeData.name === "FloatSlider-NYJY") {
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
		} else if (nodeData.name === "SeedanceVideo") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				const prefix = 'SeedanceVideo_preview_'
				const r = onExecuted ? onExecuted.apply(this, message) : undefined
				console.log("source height", this.size[1])

				if (!this.widgets) this.widgets = []

				if (this.widgets) {
					const pos = this.widgets.findIndex(w => w.name === `${prefix}_0`)
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemoved?.()
						}
						this.widgets.length = pos
					}
					if (message?.videos) {
						message.videos.forEach((params, i) => {
							const previewUrl = '/view?' + new URLSearchParams(params).toString()
							const w = this.addCustomWidget(
								createPreviewElement(
									`${prefix}_${i}`,
									previewUrl,
									"video"
								)
							)
							console.log(w)
							w.parent = this
						})
					}
					const onRemoved = this.onRemoved
					this.onRemoved = () => {
						cleanupNode(this)
						return onRemoved?.()
					}
				}
			}
		} else if (["JsonGetValueByKeys", "JsonDumps", "JsonLoads", "GetItemFromList"].includes(nodeData.name)) {
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

const createPreviewElement = (name, val, type) => {
	const w = {
		name,
		type,
		value: val,
		widgetWidth: 0,
		widgetOriginalHeight: 82,
		draw: function (ctx, node, widgetWidth) {
			this.widgetWidth = widgetWidth
			Object.assign(
				this.inputEl.style,
				get_position_style(ctx, widgetWidth - 12, this.widgetOriginalHeight)
			)

			const computedHeight = this.computeSize()[1]
			this.parent.setSize?.([widgetWidth, computedHeight]);
			// this.parent.graph?.setDirtyCanvas(true);
		},
		computeSize: function (_) {
			const ratio = this.inputRatio || 1
			return [this.widgetWidth, this.widgetWidth / ratio + this.widgetOriginalHeight]
		},
		onRemoved: function () {
			if (this.inputEl) {
				this.inputEl.remove()
			}
		}
	}
	w.inputEl = document.createElement('video')
	w.inputEl.setAttribute('type', 'video/webm')
	w.inputEl.autoplay = true
	w.inputEl.loop = true
	w.inputEl.controls = true

	w.inputEl.addEventListener('loadeddata', () => {
		w.inputRatio = w.inputEl.offsetWidth / w.inputEl.offsetHeight
	});
	document.body.appendChild(w.inputEl)
	w.inputEl.src = w.value
	return w
}


/**
 * 获取节点在页面中的绝对定位样式
 * @param {LGraphNode} n
 * @param {number} offsetX - 偏移量（默认为视觉像素）
 * @param {number} offsetY - 偏移量（默认为视觉像素）
 * @param {Object} options
 * @param {'visual'|'logical'} [options.offsetMode='visual'] - 偏移模式
 */
function get_position_style(
	ctx,
	widget_width,
	y,
) {
	/* Create a transform that deals with all the scrolling and zooming */
	const elRect = ctx.canvas.getBoundingClientRect()

	const scaleX = elRect.width / ctx.canvas.width
	const scaleY = elRect.height / ctx.canvas.height

	const transform = new DOMMatrix()
		.scaleSelf(scaleX, scaleY)
		.multiplySelf(ctx.getTransform())
		.translateSelf(6, y)

	return {
		transformOrigin: '0 0',
		transform: transform,
		left: `0`,
		top: `0`,
		cursor: 'pointer',
		position: 'absolute',
		maxWidth: `${widget_width}px`,
		// maxHeight: `${node_height - MARGIN * 2}px`, // we're assuming we have the whole height of the node
		width: `${widget_width}px`,
		zIndex: 99
	}
}

function hasWidgets(node) {
	if (!node.widgets || !node.widgets?.[Symbol.iterator]) {
		return false
	}
	return true
}

function cleanupNode(node) {
	if (!hasWidgets(node)) {
		return
	}

	for (const w of node.widgets) {
		if (w.canvas) {
			w.canvas.remove()
		}
		if (w.inputEl) {
			w.inputEl.remove()
		}
		// calls the widget remove callback
		w.onRemoved?.()
	}
}