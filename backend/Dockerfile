FROM python:3.13-slim

WORKDIR /app

# 先单独复制 requirements，利用 layer 缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码（开发模式下会被 volume 覆盖，此层仅供镜像自包含时用）
COPY . .

# 迁移 + 启动入口
RUN chmod +x entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
