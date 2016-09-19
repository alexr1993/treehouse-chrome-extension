var gulp = require("gulp");
var sourcemaps = require("gulp-sourcemaps");
var babel = require("gulp-babel");
var concat = require("gulp-concat");

gulp.task("default", ["manifest", "html"], function () {
  return gulp.src("src/**/*.js")
    .pipe(sourcemaps.init())
    .pipe(babel())
    .pipe(concat("all.js"))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("dist"));
});

gulp.task("manifest", function() {
  return gulp.src("manifest.json").pipe(gulp.dest("dist"));
});

gulp.task("html", ["res"], () => gulp.src("src/main/popup.html").pipe(gulp.dest("dist")));
gulp.task("res", () => gulp.src("res/*").pipe(gulp.dest("dist")));
