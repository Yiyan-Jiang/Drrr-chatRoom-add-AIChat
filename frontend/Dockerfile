FROM node:22-alpine

WORKDIR /app

# 先单独复制 package 文件，利用 layer 缓存
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# 复制源码（开发模式下会被 volume 覆盖）
COPY . .

# Vite dev server，绑定 0.0.0.0 让容器外可访问
EXPOSE 5173
CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "5173"]
