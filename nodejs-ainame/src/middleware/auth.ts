import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { config } from '../config';

const TOKEN_TYPE_ACCESS = '1';

export interface JwtPayload {
  iss: number;  // user id
  sub: string;  // token type
  exp: number;
}

export function authAccess(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    res.status(403).json({ detail: '缺少认证令牌' });
    return;
  }
  const token = authHeader.slice(7);
  try {
    const decoded = jwt.verify(token, config.jwtSecret) as unknown as JwtPayload;
    if (decoded.sub !== TOKEN_TYPE_ACCESS) {
      res.status(403).json({ detail: 'Token类型错误！' });
      return;
    }
    (req as Request & { userId?: number }).userId = decoded.iss;
    next();
  } catch (err: unknown) {
    if (err instanceof jwt.TokenExpiredError) {
      res.status(403).json({ detail: 'Access Token已过期！' });
      return;
    }
    res.status(403).json({ detail: 'Access Token不可用！' });
  }
}

export function encodeLoginToken(userId: number): { access_token: string; refresh_token: string } {
  const accessExp = Math.floor(Date.now() / 1000) + config.jwtAccessExpiresDays * 24 * 3600;
  const refreshExp = Math.floor(Date.now() / 1000) + config.jwtRefreshExpiresDays * 24 * 3600;
  const access_token = jwt.sign(
    { iss: userId, sub: TOKEN_TYPE_ACCESS, exp: accessExp },
    config.jwtSecret,
    { algorithm: 'HS256' }
  );
  const refresh_token = jwt.sign(
    { iss: userId, sub: '2', exp: refreshExp },
    config.jwtSecret,
    { algorithm: 'HS256' }
  );
  return { access_token, refresh_token };
}
