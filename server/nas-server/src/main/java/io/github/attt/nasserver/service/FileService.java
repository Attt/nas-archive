package io.github.attt.nasserver.service;

import io.github.attt.nasserver.model.FileVo;
import org.apache.commons.io.FileUtils;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.regex.Pattern;

@Service
public class FileService {

    /**
     * walk files and get file tree
     *
     * @param path            root path
     * @param mustContain     string that file name must contain
     * @param notContainRegex regex that file name must contain
     * @param excludeEmptyDir if empty dir should be excluded from result or not
     * @return file tree
     * @throws Throwable any throwable
     */
    public Set<FileVo> walk(String path, String mustContain, String notContainRegex, boolean excludeEmptyDir) throws Throwable {
        Pattern pattern = StringUtils.hasText(notContainRegex) ? Pattern.compile(notContainRegex) : null;
        Set<FileVo> roots = new LinkedHashSet<>();
        Map<String, FileVo> hash = new HashMap<>(); // absolute path map to all dir

        // dfs
        Files.walkFileTree(Paths.get(path), new FileVisitor<>() {
            @Override
            public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
                // create file vo for dir
                FileVo dirVo = new FileVo();
                dirVo.setDir(true);
                dirVo.setName(dir.getFileName().toString());

                update(dir, dirVo);
                hash.put(dir.getFileName().toAbsolutePath().toString(), dirVo);
                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                String fileName = file.getFileName().toString();
                if ((pattern == null || !pattern.matcher(fileName).find()) &&
                        (!StringUtils.hasText(mustContain) || fileName.contains(mustContain))) {
                    // create file vo
                    FileVo fileVo = new FileVo();
                    fileVo.setDir(false);
                    fileVo.setName(fileName);
                    fileVo.setSize(FileUtils.byteCountToDisplaySize(file.toFile().length()));
                    fileVo.setBytes(file.toFile().length());

                    update(file, fileVo);
                }
                return FileVisitResult.CONTINUE;
            }

            /**
             * try to find parent file vo and join in the children set of it.
             * otherwise update self as a new parent file vo
             *
             * @param fileOrDir file or dir path
             * @param fileVo the file vo
             */
            private void update(Path fileOrDir, FileVo fileVo) {
                String parentPath = fileOrDir.getParent().getFileName().toAbsolutePath().toString();
                FileVo parent = hash.getOrDefault(parentPath, null);
                if (parent != null) {
                    if (parent.getChildren() == null) parent.setChildren(new LinkedHashSet<>());
                    parent.getChildren().add(fileVo);
                } else roots.add(fileVo);
            }

            @Override
            public FileVisitResult visitFileFailed(Path file, IOException exc) throws IOException {
                return FileVisitResult.TERMINATE;
            }

            @Override
            public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
                return FileVisitResult.CONTINUE;
            }
        });

        if (excludeEmptyDir) roots.removeIf(this::removeEmptyDir);
        return roots;
    }

    // TODO: 2022/9/18
//    public Set<FileVo> transferFiles(List<String> absolutePaths, ) {
//
//    }

    /**
     * remove all empty directories recursively
     *
     * @param root file vo
     * @return if param should be removed or not
     */
    private boolean removeEmptyDir(FileVo root) {
        if (root == null || CollectionUtils.isEmpty(root.getChildren())) return true;
        Set<FileVo> children = root.getChildren();
        children.removeIf(next -> next.isDir() && removeEmptyDir(next)); // post-ordered traverse
        return CollectionUtils.isEmpty(root.getChildren());
    }

}
