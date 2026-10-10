package com.zhiliao.ainame.repository;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zhiliao.ainame.entity.AppUser;
import java.util.Optional;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface AppUserRepository extends BaseRepository<AppUser> {
    default boolean existsByEmail(String email) { return selectCount(Wrappers.<AppUser>query().eq("email", email)) > 0; }
    default Optional<AppUser> findByEmail(String email) { return Optional.ofNullable(selectOne(Wrappers.<AppUser>query().eq("email", email).last("LIMIT 1"))); }
}
