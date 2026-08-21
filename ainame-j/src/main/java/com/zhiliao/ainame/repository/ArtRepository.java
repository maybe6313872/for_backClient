package com.zhiliao.ainame.repository;

import com.zhiliao.ainame.entity.Art;
import java.util.Collection;
import java.util.List;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ArtRepository extends JpaRepository<Art, Integer> {
    List<Art> findBySexOrderByCreatedTimeDesc(String sex, Pageable pageable);

    long deleteByIdIn(Collection<Integer> ids);
}
