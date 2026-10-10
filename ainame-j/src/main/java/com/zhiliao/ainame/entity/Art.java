package com.zhiliao.ainame.entity;

import java.time.LocalDateTime;
import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@TableName("art")
public class Art implements PersistedEntity {
    @TableId(type = IdType.AUTO)
    private Integer id;

    private String username = "";

    private String sex = "";

    private String artcontent = "";

    private byte[] thumbnail = new byte[0];

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;

}
