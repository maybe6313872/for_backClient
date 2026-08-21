/**
 * 应用配置
 * 从环境变量读取，提供默认值
 */

function env(key: string, defaultValue: string): string {
  return process.env[key] ?? defaultValue;
}

function envInt(key: string, defaultValue: number): number {
  const v = process.env[key];
  return v ? parseInt(v, 10) : defaultValue;
}

function envBool(key: string, defaultValue: boolean): boolean {
  const v = process.env[key];
  if (v === undefined || v === '') return defaultValue;
  return v.toLowerCase() === 'true' || v === '1';
}

export const config = {
  // 数据库
  databaseUrl: env(
    'DATABASE_URL',
    'mysql://root:root@127.0.0.1:3306/zhiliao_ainame?charset=utf8mb4'
  ),

  // Redis
  redisUrl: env('REDIS_URL', 'redis://localhost:6379/0'),

  // JWT
  jwtSecret: env('JWT_SECRET_KEY', 'sfsadadafsjw'),
  jwtAccessExpiresDays: envInt('JWT_ACCESS_TOKEN_EXPIRES_DAYS', 15),
  jwtRefreshExpiresDays: envInt('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30),

  // 邮件
  mail: {
    username: env('MAIL_USERNAME', ''),
    password: env('MAIL_PASSWORD', ''),
    from: env('MAIL_FROM', ''),
    fromName: env('MAIL_FROM_NAME', '知了课堂'),
    server: env('MAIL_SERVER', 'smtp.qq.com'),
    port: envInt('MAIL_PORT', 587),
    starttls: envBool('MAIL_STARTTLS', true),
    sslTls: envBool('MAIL_SSL_TLS', false),
  },

  // 可选：AI
  deepseekApiKey: env('DEEPSEEK_API_KEY', ''),
};
