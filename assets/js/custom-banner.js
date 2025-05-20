document.addEventListener('DOMContentLoaded', function () {
  const banner = document.querySelector('.home-banner-page .page__hero--overlay');
  if (!banner) return;

  let lastScrollTop = 0;

  window.addEventListener('scroll', function () {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const collapsePoint = window.innerHeight * 1 / 4;
    const bannerRect = banner.getBoundingClientRect();
    const bannerBottomRelativeToViewport = bannerRect.bottom;

    if (scrollTop <= 5) { // If at the very top (added a small buffer of 5px)
      banner.classList.remove('banner-hidden');
    } else if (scrollTop > lastScrollTop) {
      // 向下滚动
      if (bannerBottomRelativeToViewport < collapsePoint) {
        banner.classList.add('banner-hidden');
      }
    } else if (scrollTop < lastScrollTop) {
      // 向上滚动
      if (bannerBottomRelativeToViewport >= collapsePoint) {
        banner.classList.remove('banner-hidden');
      }
    }
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  }, false);
}); 