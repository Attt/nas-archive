package io.github.attt.nasserver.controller;

import com.apptasticsoftware.rssreader.Item;
import com.apptasticsoftware.rssreader.RssReader;
import io.github.attt.nasserver.model.RssFeedVo;
import io.github.attt.nasserver.model.RssFeedTorrentVo;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import java.io.*;
import java.sql.Timestamp;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Rss feed controller
 *
 * @author atpex
 */
@RestController
public class RssController {

    @GetMapping("/hello")
    public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {

        return String.format("Hello %s!", name);
    }

    RssReader reader = new RssReader();

    @GetMapping("/readRssFeed")
    @ResponseBody
    public RssFeedVo readRssFeed(@RequestParam(value = "rss") String rss, @RequestParam(value = "type", defaultValue = "filter") int type) throws IOException {
        RssFeedVo feed = new RssFeedVo();
        feed.setTitle(rss);
//        Stream<Item> rssFeed = reader.read(new ByteArrayInputStream());
        Stream<Item> rssFeed = reader.read(rss);
        List<Item> items = rssFeed.toList();
        feed.setTorrents(items.stream().map(item -> {
            RssFeedTorrentVo feedTorrent = new RssFeedTorrentVo();
            feedTorrent.setName(item.getTitle().get());
            feedTorrent.setPubDate(Timestamp.valueOf(item.getPubDate().get().replace("T", " ")).getTime());
            feedTorrent.setLink(item.getEnclosure().get().getUrl());
            return feedTorrent;
        }).collect(Collectors.toList()));
        return feed;
    }

}
