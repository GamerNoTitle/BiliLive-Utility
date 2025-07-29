class BiliLiveUtility {
    constructor() {
        this.qrTimer = null
        this.countdownTimer = null
        this.countdownSeconds = 180
        this.isLive = false
        this.areas = []
        this.prevTitle = ""
        this.prevTags = []

        this.init()
    }

    init() {
        this.bindEvents()
        this.checkFirstVisit()
        this.loadAreas()
    }

    // Toast 相关方法
    showToast(message, type = "info", duration = 3000) {
        const container = document.getElementById("toastContainer")
        const toast = document.createElement("div")
        toast.className = `toast ${type}`

        const iconMap = {
            success: "fas fa-check-circle",
            error: "fas fa-exclamation-circle",
            warning: "fas fa-exclamation-triangle",
            info: "fas fa-info-circle",
        }

        toast.innerHTML = `
      <i class="${iconMap[type]} toast-icon"></i>
      <span class="toast-message">${message}</span>
      <button class="toast-close">&times;</button>
    `

        container.appendChild(toast)

        // 关闭按钮事件
        const closeBtn = toast.querySelector(".toast-close")
        closeBtn.addEventListener("click", () => this.removeToast(toast))

        // 自动关闭
        setTimeout(() => {
            this.removeToast(toast)
        }, duration)
    }

    removeToast(toast) {
        if (toast && toast.parentNode) {
            toast.classList.add("removing")
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast)
                }
            }, 300)
        }
    }

    bindEvents() {
        // 免责声明
        document.getElementById("agreeBtn").addEventListener("click", () => this.acceptDisclaimer())
        document.getElementById("disagreeBtn").addEventListener("click", () => this.rejectDisclaimer())

        // 登录相关
        document.getElementById("refreshQr").addEventListener("click", () => this.generateQRCode())

        // 主页面功能
        document.getElementById("getRoomData").addEventListener("click", () => this.getRoomData())
        document.getElementById("updateTitle").addEventListener("click", () => this.updateRoomTitle())
        document.getElementById("updateTags").addEventListener("click", () => this.updateRoomTags())
        document.getElementById("updateArea").addEventListener("click", () => this.updateRoomArea())
        document.getElementById("liveToggle").addEventListener("click", () => this.toggleLive())
        document.getElementById("copyAddr").addEventListener("click", () => this.copyToClipboard("streamAddr"))
        document.getElementById("copyCode").addEventListener("click", () => this.copyToClipboard("streamCode"))
        document.getElementById("saveCredentials").addEventListener("click", () => this.saveStreamCredentials())

        // 分区选择
        document.getElementById("parentArea").addEventListener("change", () => this.onParentAreaChange())

        // 关于页面
        document.getElementById("aboutBtn").addEventListener("click", () => this.showAbout())
        document.querySelector(".modal-close").addEventListener("click", () => this.hideAbout())

        // 关闭按钮
        document.getElementById("closeBtn").addEventListener("click", () => {
            fetch("/api/application/exit")
            this.showStatus("正在退出应用...", "info")
        })

        // 点击模态框外部关闭
        document.getElementById("aboutModal").addEventListener("click", (e) => {
            if (e.target === document.getElementById("aboutModal")) {
                this.hideAbout()
            }
        })
    }

    async checkFirstVisit() {
        // 检查是否是首次访问以及初始化
        var firstAccess = true
        const data = await (await fetch("/api/application/info")).json().then(data => data.data)
        this.isLive = data.account.is_live || false
        if (this.isLive) {
            const button = document.getElementById("liveToggle")
            button.innerHTML = '<i class="fas fa-stop"></i> 停播'
            button.classList.add("stop")
        }
        if (data.first_access === undefined) {
        } else {
            firstAccess = data.first_access
        }
        const version = data.version
        if (!firstAccess) {
            document.getElementById("disclaimerModal").style.display = "flex"
        } else {
            this.checkLoginStatus()
        }
        document.getElementById("version").textContent = `${version}`
    }

    async acceptDisclaimer() {
        await fetch("/api/application/first_access")
        document.getElementById("disclaimerModal").style.display = "none"
        this.checkLoginStatus()
    }

    rejectDisclaimer() {
        fetch("/api/application/disagree")
        document.getElementById("disclaimerModal").style.display = "none"
        this.showToast("用户拒绝免责声明，程序即将退出", "error")
    }

    async checkLoginStatus() {
        // 检查登录状态
        const isLoggedIn = await (await fetch("/api/auth/check_login")).json().then(data => data.success)

        if (isLoggedIn) {
            // 已登录，显示主页面
            this.showMainPage()
            document.getElementById("liveToggle").classList.remove("hidden")
            // 填充直播间号和 Cookies
            const credentials = await (await fetch("/api/auth/credentials")).json().then(data => data.data)
            const roomId = credentials.room_id || ""
            const cookies = credentials.cookies || ""
            document.getElementById("roomId").value = roomId
            document.getElementById("cookies").value = cookies
        } else {
            // 未登录，显示登录页面
            this.showLoginPage()
        }
    }

    showLoginPage() {
        document.getElementById("loginPage").classList.remove("hidden")
        document.getElementById("mainPage").classList.add("hidden")
        this.generateQRCode()
    }

    showMainPage() {
        document.getElementById("loginPage").classList.add("hidden")
        document.getElementById("mainPage").classList.remove("hidden")
    }

    async generateQRCode() {
        try {
            this.showStatus("正在生成二维码...", "info")

            const response = await fetch("/api/auth/getcode")

            if (response.ok) {
                const data = await response.json()
                this.displayQRCode(data.data.url)
                this.qrKey = data.data.qrcode_key
                this.startQRPolling(this.qrKey)
                this.startCountdown()
            } else {
                throw new Error("生成二维码失败")
            }
        } catch (error) {
            console.error("生成二维码失败:", error)
            // 使用占位符二维码
            this.displayPlaceholderQR()
        }
    }

    async displayQRCode(url) {
        const qrContainer = document.getElementById("qrCode")
        const qrImage = await (await fetch("/api/auth/getqr?link=" + encodeURIComponent(url))).json().then(data => data.data)
        qrContainer.innerHTML = `<img src="data:image/png;base64,${qrImage}" alt="登录二维码" style="width: 100%; height: 100%; object-fit: contain;">`
        document.getElementById("qrStatus").textContent = "请使用B站手机客户端扫码登录"
    }

    displayPlaceholderQR() {
        const qrContainer = document.getElementById("qrCode")
        qrContainer.innerHTML = `
            <i class="fas fa-qrcode"></i>
            <p>二维码生成失败，请刷新重试</p>
        `
    }

    startCountdown() {
        // 清除旧的计时器
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer)
        }

        this.countdownSeconds = 180
        document.getElementById("countdown").textContent = this.countdownSeconds // 立即更新一次UI

        this.countdownTimer = setInterval(() => {
            this.countdownSeconds--
            document.getElementById("countdown").textContent = this.countdownSeconds

            if (this.countdownSeconds <= 0) {
                clearInterval(this.countdownTimer)
                this.generateQRCode()
            }
        }, 1000)
    }

    async startQRPolling(qrKey) {
        if (this.qrTimer) {
            clearInterval(this.qrTimer)
        }

        this.qrTimer = setInterval(async () => {
            try {
                const response = await fetch(`/api/auth/poll?qrcode_key=${qrKey}`)

                if (response.ok) {
                    const data = await response.json()
                    this.handleQRStatus(data)
                }
            } catch (error) {
                console.error("轮询失败:", error)
            }
        }, 2000)
    }

    handleQRStatus(data) {
        const statusElement = document.getElementById("qrStatus")

        switch (data.data.code) {
            case 0: // 登录成功
                this.handleLoginSuccess(data.data)
                break
            case 86101: // 未扫码
                statusElement.textContent = "等待扫码中..."
                break
            case 86090: // 已扫码未确认
                statusElement.textContent = "已扫码，请在手机上确认登录"
                break
            default:
                statusElement.textContent = `状态：${data.message}`
        }
    }

    handleLoginSuccess(data) {
        clearInterval(this.qrTimer)
        clearInterval(this.countdownTimer)

        this.showStatus("登录成功！正在跳转...", "success")

        setTimeout(() => {
            this.showMainPage()
            document.getElementById("cookies").value = data.data.cookies
            document.getElementById("roomId").value = data.data.room_id
            document.getElementById("liveToggle").classList.remove("hidden")
        }, 1500)
    }

    async loadAreas() {
        try {
            const areas = await (await fetch("/api/room/areas")).json().then(data => data.data)
            // 拆解 areas 数据
            // data 里面是每个父分区，父分区下的 list 是子分区
            // 获取父分区的 id 和 name 并组合为 {name}(id) 的格式
            // 再获取每个父分区下的子分区的 id 和 name 并组合为 {name}(id) 的格式
            this.areas = areas.map(area => ({
                id: area.id,
                name: area.name,
                list: area.list.map(subArea => ({
                    id: subArea.id,
                    name: subArea.name
                }))
            }))
            this.populateParentAreas()
        } catch (error) {
            console.error("加载分区失败:", error)
        }
    }

    populateParentAreas() {
        // 填充父分区下拉框
        const areas = this.areas.filter(area => area.list && area.list.length > 0)
        if (areas.length === 0) {
            const parentAreaSelect = document.getElementById("parentArea")
            parentAreaSelect.innerHTML = '<option value="">-- 请选择父分区 --</option>'
        }
        const parentAreaSelect = document.getElementById("parentArea")
        parentAreaSelect.innerHTML = '<option value="">-- 请选择父分区 --</option>'
        areas.forEach(area => {
            const option = document.createElement("option")
            option.value = area.id
            option.textContent = `${area.name}(${area.id})`
            parentAreaSelect.appendChild(option)
        })
    }

    onParentAreaChange() {
        const parentAreaId = Number.parseInt(document.getElementById("parentArea").value)
        const childAreaSelect = document.getElementById("childArea")

        childAreaSelect.innerHTML = '<option value="">-- 请选择子分区 --</option>'

        if (parentAreaId) {
            const parentArea = this.areas.find((area) => area.id === parentAreaId)
            if (parentArea && parentArea.list) {
                parentArea.list.forEach((subArea) => {
                    const option = document.createElement("option")
                    option.value = subArea.id
                    option.textContent = `${subArea.name}(${subArea.id})`
                    childAreaSelect.appendChild(option)
                })
            }
        }
    }

    async getRoomData() {
        try {
            const response = await fetch("/api/room/info")

            if (response.ok) {
                const data = await response.json()
                this.populateRoomData(data)
                this.showStatus("成功获取直播间信息！", "success")
            } else {
                throw new Error("获取直播间信息失败")
            }
        } catch (error) {
            console.error("获取直播间信息失败:", error)
            this.showStatus("获取直播间信息失败！", "error")
        }
    }

    populateRoomData(data) {
        document.getElementById("roomTitle").value = data.data.title
        document.getElementById("roomTags").value = data.data.tags.join(", ")

        // 设置分区
        document.getElementById("parentArea").value = data.data.area.parent_id
        this.onParentAreaChange()

        setTimeout(() => {
            document.getElementById("childArea").value = data.data.area.id
        }, 100)

        this.prevTitle = data.title
        this.prevTags = data.tags
    }

    async updateRoomTitle() {
        const title = document.getElementById("roomTitle").value.trim()
        const roomId = document.getElementById("roomId").value.trim()
        const cookies = document.getElementById("cookies").value.trim()

        if (!this.validateInputs(roomId, cookies, title, "直播间标题")) return
        if (title.length > 41) {
            this.showStatus("错误：直播间标题长度不能超过 41 个字符！", "error")
            return
        }

        this.showLoading(true)

        try {
            const response = await fetch("/api/room/info", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title }),
            })

            if (response.ok) {
                this.showStatus("更新直播间标题成功！", "success")
                this.showToast("直播间标题已保存", "success")
                this.prevTitle = title
            } else {
                throw new Error("更新失败")
            }
        } catch (error) {
            console.error("更新标题失败:", error)
            this.showToast("直播间标题更新失败", "error")
        } finally {
            this.showLoading(false)
        }
    }

    async updateRoomTags() {
        const tagsStr = document.getElementById("roomTags").value.trim()
        const roomId = document.getElementById("roomId").value.trim()
        const cookies = document.getElementById("cookies").value.trim()

        if (!this.validateInputs(roomId, cookies, tagsStr, "直播间标签")) return

        const tags = tagsStr
            .replace(/，/g, ",")
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag)

        for (const tag of tags) {
            if (tag.length > 20) {
                this.showStatus(`错误：标签 "${tag}" 长度不能超过 20 个字符！`, "error")
                return
            }
        }

        this.showLoading(true)
        this.showStatus("因为B站对操作有频率限制，所以修改标签需要的时间较久，请耐心等待！", "warning")

        try {
            const response = await fetch("/api/room/info", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ tags }),
            })

            if (response.ok) {
                this.showStatus("更新直播间标签成功！", "success")
                this.showToast("直播间标签已保存", "success")
                this.prevTags = tags
            } else {
                throw new Error("更新失败")
            }
        } catch (error) {
            console.error("更新标签失败:", error)
            this.showToast("直播间标签更新失败", "error")
            this.showStatus("更新直播间标签失败！", "error")
        } finally {
            this.showLoading(false)
        }
    }

    async updateRoomArea() {
        const areaId = document.getElementById("childArea").value
        const parentAreaId = document.getElementById("parentArea").value
        const roomId = document.getElementById("roomId").value.trim()
        const cookies = document.getElementById("cookies").value.trim()

        if (!areaId) {
            this.showStatus("错误：请选择直播间分区！", "error")
            return
        }

        if (!this.validateInputs(roomId, cookies)) return

        this.showLoading(true)

        try {
            const response = await fetch("/api/room/info", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    area: {
                        area: Number.parseInt(parentAreaId),
                        sub_area: Number.parseInt(areaId),
                    },
                }),
            })

            if (response.ok) {
                this.showStatus("更新直播间分区成功！", "success")
                this.showToast("直播间分区已保存", "success")
            } else {
                throw new Error("更新失败")
            }
        } catch (error) {
            console.error("更新分区失败:", error)
            this.showToast("直播间分区更新失败", "error")
            this.showStatus("更新直播间分区失败！", "error")
        } finally {
            this.showLoading(false)
        }
    }

    async toggleLive() {
        const roomId = document.getElementById("roomId").value.trim()
        const cookies = document.getElementById("cookies").value.trim()

        if (!this.validateInputs(roomId, cookies)) return

        const button = document.getElementById("liveToggle")
        const isStarting = !this.isLive

        this.showLoading(true)

        if (isStarting) {
            const areaId = document.getElementById("childArea").value
            if (!areaId) {
                this.showStatus("请先获取直播间信息后再开播！", "error")
                this.showLoading(false)
                return
            }
        }

        try {
            const endpoint = isStarting ? "/api/live/start" : "/api/live/stop"
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: isStarting ? JSON.stringify({ area: document.getElementById("childArea").value }) : null,
            })

            if (response.ok) {
                if (isStarting) {
                    const data = await response.json()
                    this.handleLiveStart(data)
                } else {
                    this.handleLiveStop()
                }
            } else {
                this.showStatus(`${(await response.json()).data.error}`, "error")
                this.showToast(`${isStarting ? "开播" : "停播"}失败`, "error")
            }
        } catch (error) {
            console.error(`${isStarting ? "开播" : "停播"}失败:`, error)
            this.showStatus(`${isStarting ? "开播" : "停播"}失败！`, "error")
        } finally {
            this.showLoading(false)
        }
    }

    handleLiveStart(data) {
        this.isLive = true
        const button = document.getElementById("liveToggle")
        button.innerHTML = '<i class="fas fa-stop"></i> 停播'
        button.classList.add("stop")

        document.getElementById("streamAddr").value = data.data.rtmp.addr
        document.getElementById("streamCode").value = data.data.rtmp.code

        this.showStatus("开播成功！推流信息已显示。", "success")
    }

    handleLiveStop() {
        this.isLive = false
        const button = document.getElementById("liveToggle")
        button.innerHTML = '<i class="fas fa-play"></i> 开播'
        button.classList.remove("stop")

        this.showStatus("停播成功！", "success")
    }

    saveStreamCredentials() {
        const roomId = document.getElementById("roomId").value
        const addr = document.getElementById("streamAddr").value
        const code = document.getElementById("streamCode").value

        if (!addr || !code) {
            this.showToast("推流信息为空，请先开播", "warning")
            return
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
        const filename = `stream_info_${roomId}_${timestamp}.txt`

        const content = `直播间号: ${roomId}\n推流地址: ${addr}\n推流密钥: ${code}\n生成时间: ${new Date().toLocaleString()}`

        const blob = new Blob([content], { type: "text/plain" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = filename
        a.click()
        URL.revokeObjectURL(url)

        this.showToast("推流凭据已保存到本地", "success")
    }

    copyToClipboard(elementId) {
        const element = document.getElementById(elementId)
        const text = element.value

        if (!text) {
            this.showStatus("内容为空，无法复制！", "error")
            return
        }

        navigator.clipboard
            .writeText(text)
            .then(() => {
                const type = elementId === "streamAddr" ? "推流地址" : "推流密钥"
                this.showToast(`${type}已复制到剪贴板`, "success")
            })
            .catch(() => {
                this.showToast("复制失败，请手动复制", "error")
            })
    }

    validateInputs(roomId, cookies, content = null, contentName = null) {
        if (!roomId) {
            this.showStatus("错误：直播间号不能为空！", "error")
            return false
        }
        if (!cookies) {
            this.showStatus("错误：Cookies 不能为空！", "error")
            return false
        }
        if (content !== null && !content) {
            this.showStatus(`错误：${contentName}不能为空！`, "error")
            return false
        }
        return true
    }

    showStatus(message, type = "info") {
        const statusElement = document.getElementById("statusMessage")
        const iconMap = {
            info: "fas fa-info-circle",
            success: "fas fa-check-circle",
            error: "fas fa-exclamation-circle",
            warning: "fas fa-exclamation-triangle",
        }

        statusElement.className = `status-message ${type}`
        statusElement.innerHTML = `<i class="${iconMap[type]}"></i><span>${message}</span>`
    }

    showLoading(show) {
        const overlay = document.getElementById("loadingOverlay")
        if (show) {
            overlay.classList.remove("hidden")
        } else {
            overlay.classList.add("hidden")
        }
    }

    showAbout() {
        document.getElementById("aboutModal").classList.remove("hidden")
    }

    hideAbout() {
        document.getElementById("aboutModal").style.display = "none"
    }
}

// 初始化应用
document.addEventListener("DOMContentLoaded", () => {
    new BiliLiveUtility()
})
