package io.github.attt.nasserver.model;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;
import lombok.Data;

import java.util.LinkedList;
import java.util.List;
import java.util.Set;

@Data
public class FileVo {

    @SerializedName("file name")
    @Expose
    private String name;

    @Expose(serialize = false, deserialize = false)
    private long bytes;

    @SerializedName("file size")
    @Expose
    private String size; // human readable

    @Expose(serialize = false, deserialize = false)
    private boolean isDir;

    @SerializedName("-")
    @Expose
    private Set<FileVo> children; // file tree
}
