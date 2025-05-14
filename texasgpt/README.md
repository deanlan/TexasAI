# TexasGPT 后端服务

TexasGPT 是 TexasAI 项目的后端服务组件，基于 Python 和 FastAPI 构建。

## 启动服务

请按照以下步骤启动后端服务：

1.  **赋予执行权限** (仅首次运行或脚本权限丢失时需要):
    打开终端，并导航到 `texasgpt` 目录，然后运行以下命令：
    ```bash
    chmod +x start.sh
    ```

2.  **启动服务**:
    在 `texasgpt` 目录下，运行启动脚本：
    ```bash
    ./start.sh
    ```

服务启动后，默认将在 `http://localhost:5670` (或由 `start.sh` 及应用配置中指定的端口) 上监听请求。

## 注意事项

-   确保您已按照项目根目录 `README.md` 中的说明安装了所有必要的依赖项 (例如，通过 `poetry install`)。
-   如果服务端口 (`5670`) 已被占用，您可能需要修改 `start.sh` 脚本或 FastAPI 应用配置中的端口设置。