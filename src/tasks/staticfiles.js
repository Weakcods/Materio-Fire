const path = require('path');
const { src, dest, series, parallel } = require('gulp');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const rename = require('gulp-rename');
const imagemin = require('gulp-imagemin');

module.exports = conf => {
  // Minify CSS files
  const minifyCssTask = function () {
    return src(`${conf.distPath}/css/**/*.css`)
      .pipe(cleanCSS())
      .pipe(rename({ suffix: '.min' }))
      .pipe(dest(`${conf.distPath}/css`));
  };

  // Minify JS files
  const minifyJsTask = function () {
    return src([`${conf.distPath}/js/**/*.js`, `!${conf.distPath}/js/**/*.min.js`])
      .pipe(uglify())
      .pipe(rename({ suffix: '.min' }))
      .pipe(dest(`${conf.distPath}/js`));
  };

  // Optimize images
  const optimizeImagesTask = function () {
    return src(`${conf.distPath}/img/**/*.{png,jpg,jpeg,gif,svg}`)
      .pipe(imagemin())
      .pipe(dest(`${conf.distPath}/img`));
  };

  // Combine all tasks
  const staticFilesTask = parallel(minifyCssTask, minifyJsTask, optimizeImagesTask);

  return {
    css: minifyCssTask,
    js: minifyJsTask,
    images: optimizeImagesTask,
    all: staticFilesTask
  };
};
