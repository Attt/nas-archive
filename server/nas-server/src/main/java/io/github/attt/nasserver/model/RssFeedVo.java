package io.github.attt.nasserver.model;

import lombok.Data;

import java.util.List;

@Data
public class RssFeedVo {

    public RssFeedVo() {
        this.fetchDate = System.currentTimeMillis();
    }

    private String title;
    private long fetchDate;
    private List<RssFeedTorrentVo> torrents;
}
