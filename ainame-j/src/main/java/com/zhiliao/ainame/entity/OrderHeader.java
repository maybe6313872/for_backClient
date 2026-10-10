package com.zhiliao.ainame.entity;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
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
@TableName("`order`")
public class OrderHeader implements PersistedEntity {
    @TableId(type = IdType.AUTO)
    private Integer id;

    private String orderNumber = "";

    private Integer companyId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdTime;

    @TableField(exist = false)
    private Company company;

    @TableField(exist = false)
    private List<OrderLine> orderLines = new ArrayList<>();

}
