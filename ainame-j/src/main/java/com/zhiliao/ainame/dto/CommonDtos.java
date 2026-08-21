package com.zhiliao.ainame.dto;

public final class CommonDtos {
    private CommonDtos() {
    }

    public record ResponseOut(String result) {
        public ResponseOut() {
            this("success");
        }
    }

    public record ApiMessage(int code, String message, Object data) {
        public ApiMessage(Object data) {
            this(200, "查询成功", data);
        }
    }
}
