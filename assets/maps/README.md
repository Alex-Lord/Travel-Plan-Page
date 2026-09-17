# Fixed Map Templates

普通旅行生成只使用 `templates/manifest.json` 中登记的十张固定底图。Manifest 的运行时路径全部指向 WebP；底图负责纸张、地形、水体、山林和整体构图，路线、节点、地点标签、目的地标题及日期图例始终由固定 Renderer 叠加。

1. `inland-alpine`：均衡或东西向路线。
2. `island-archipelago`：分离地点簇或存在明显长距离跳转。
3. `coastal-region`：以南北方向为主的路线。
4. `urban-radial`：单城市、紧凑或高密度点位。
5. `river-highland`：均衡路线或分离地点簇。
6. `upland-basin`：紧凑或均衡路线。
7. `compact-basin`：紧凑或高密度点位。
8. `wide-valley`：东西向路线。
9. `radial-watershed`：南北向或放射型路线。
10. `broad-riverland`：大跨度或多站路线。

Builder 先根据地点经纬度、路线跨度、方向、密度和连通关系形成候选池，再使用由区域、地点与路线组成的旅行签名稳定哈希，从候选池中确定性选择一张。Manifest 中的 `selectionRole` 只是维护说明，Builder 不会直接解析这些字符串作为选择规则。Agent 不得自行选择视觉风格、生成新底图、重画国家轮廓或修改模板安全区域。

十张图片均作为本项目的固定静态模板资产；普通生成不得覆盖这些文件。

`aster-isles-base.png`、`mist-coast-base.png`、`generic-diagram-template.svg` 与 `generated-japan.svg` 仅作为旧实现参考保留，不再进入默认 Builder 链路。

## 悉尼定制底图

`sydney-user-base.png` 是用户明确提供并授权用于本项目的原图（1448 × 1086），未裁剪、重绘或改变比例。它是未经地理标定的艺术底图，不宣称道路、海岸或标记具有导航精度。

后续 DIY 模式可在私有输入 `map.customArtwork` 中指定 `file` 与 `panels`，在 `map.places[].artworkPosition` 中指定插图坐标和标签位置。继续运行 `npm run build:map` 生成总览和每日路线，再重新加密发布。该选项不修改十张默认模板或默认的自动布局。

蓝山采用独立示意小窗；不同 `panel` 的点之间不画跨窗连线，避免暗示它紧邻悉尼城区。真实经纬度和导航查询仍保留。原始行程及定制坐标仅随加密数据发布。
