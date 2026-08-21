package com.zhiliao.ainame.service;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class JwtTokenService {
    private static final String ACCESS_SUB = "1";
    private static final String REFRESH_SUB = "2";

    private final String secretKey;
    private final int accessTokenDays;
    private final int refreshTokenDays;

    public JwtTokenService(
        @Value("${app.jwt.secret-key}") String secretKey,
        @Value("${app.jwt.access-token-days}") int accessTokenDays,
        @Value("${app.jwt.refresh-token-days}") int refreshTokenDays
    ) {
        this.secretKey = secretKey;
        this.accessTokenDays = accessTokenDays;
        this.refreshTokenDays = refreshTokenDays;
    }

    public String createAccessToken(Integer userId) {
        return encode(userId, ACCESS_SUB, accessTokenDays);
    }

    public String createRefreshToken(Integer userId) {
        return encode(userId, REFRESH_SUB, refreshTokenDays);
    }

    public LoginTokens createLoginTokens(Integer userId) {
        return new LoginTokens(createAccessToken(userId), createRefreshToken(userId));
    }

    public Integer getUserIdFromAccessToken(String token) {
        return decode(token, ACCESS_SUB, "Access Token不可用！");
    }

    public Integer getUserIdFromRefreshToken(String token) {
        return decode(token, REFRESH_SUB, "Refresh Token不可用！");
    }

    private String encode(Integer userId, String subject, int validDays) {
        var expiresAt = Date.from(Instant.now().plus(validDays, ChronoUnit.DAYS));
        return JWT.create()
            .withIssuer(String.valueOf(userId))
            .withSubject(subject)
            .withExpiresAt(expiresAt)
            .sign(Algorithm.HMAC256(secretKey));
    }

    private Integer decode(String token, String expectedSubject, String invalidMessage) {
        try {
            JWTVerifier verifier = JWT.require(Algorithm.HMAC256(secretKey))
                .withSubject(expectedSubject)
                .build();
            DecodedJWT jwt = verifier.verify(token);
            return Integer.parseInt(jwt.getIssuer());
        } catch (JWTVerificationException | NumberFormatException ex) {
            throw new IllegalArgumentException(invalidMessage, ex);
        }
    }

    public record LoginTokens(String accessToken, String refreshToken) {
    }
}
