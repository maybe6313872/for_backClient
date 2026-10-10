package com.zhiliao.ainame.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.zhiliao.ainame.entity.PersistedEntity;
import java.util.List;
import java.util.Optional;

/** Shared CRUD conveniences replacing the former Spring Data JPA repository base. */
public interface BaseRepository<T extends PersistedEntity> extends BaseMapper<T> {
    default boolean save(T entity) {
        return entity.getId() == null ? insert(entity) > 0 : updateById(entity) > 0;
    }

    default Optional<T> findById(Integer id) {
        return Optional.ofNullable(selectById(id));
    }

    default List<T> findAll() {
        return selectList(Wrappers.emptyWrapper());
    }

    default boolean delete(T entity) {
        return entity.getId() != null && deleteById(entity.getId()) > 0;
    }
}
